"""pass2rule 工具：使用 PTN Transformer 预测口令变换规则。"""
from __future__ import annotations

import asyncio
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any

from agent.graph import register_tool
from agent.state import PassAgentState
from config import (
    PASS2RULE_CHECKPOINT_PATH,
    PASS2RULE_DEVICE,
    PASS2RULE_MODEL_DIR,
)

DEFAULT_TOP_K = 20
DEFAULT_BEAM_SIZE = 100
DEFAULT_LABEL_BUDGET = 500
DEFAULT_DECODE_LEN = 30
MAX_TOP_K = 50
MAX_BEAM_SIZE = 200
MAX_LABEL_BUDGET = 1000
MAX_DECODE_LEN = 60


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _bool_param(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


class _Pass2RulePredictor:
    """Lazy runtime wrapper so normal backend imports do not require torch."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runtime_loaded = False
        self._torch: Any = None
        self._ptn: Any = None
        self._beam_search: Any = None
        self._constrained_beam_search: Any = None
        self._load_checkpoint: Any = None
        self._model: Any = None
        self._state: dict[str, Any] = {}
        self._device: Any = None
        self._checkpoint_path: Path | None = None
        self._max_src_len = 40

    def _choose_device(self) -> Any:
        device_name = PASS2RULE_DEVICE
        torch = self._torch
        if device_name == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            if (
                getattr(torch.backends, "mps", None) is not None
                and torch.backends.mps.is_available()
            ):
                return torch.device("mps")
            return torch.device("cpu")
        return torch.device(device_name)

    def _load_runtime(self) -> None:
        if self._runtime_loaded:
            return

        with self._lock:
            if self._runtime_loaded:
                return

            model_dir = Path(PASS2RULE_MODEL_DIR).expanduser().resolve()
            checkpoint_path = Path(PASS2RULE_CHECKPOINT_PATH).expanduser().resolve()

            if not model_dir.exists():
                raise RuntimeError(f"Pass2Rule 模型目录不存在: {model_dir}")
            if not checkpoint_path.exists():
                raise RuntimeError(f"Pass2Rule checkpoint 不存在: {checkpoint_path}")

            try:
                import torch
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "缺少 torch 依赖，无法运行 Pass2Rule PTN 模型。"
                    "请在 backend 目录执行 `uv sync`，或安装 PyTorch 后重试。"
                ) from exc

            if str(model_dir) not in sys.path:
                sys.path.insert(0, str(model_dir))

            try:
                from src import ptn as ptn_module
                from src.modeling import (
                    beam_search,
                    constrained_beam_search,
                    load_checkpoint,
                )
            except Exception as exc:
                raise RuntimeError(
                    f"无法导入 Pass2Rule 推理代码，请检查 {model_dir}/src 是否完整。"
                ) from exc

            self._torch = torch
            self._ptn = ptn_module
            self._beam_search = beam_search
            self._constrained_beam_search = constrained_beam_search
            self._load_checkpoint = load_checkpoint
            self._device = self._choose_device()
            self._model, self._state = self._load_checkpoint(checkpoint_path, self._device)
            self._checkpoint_path = checkpoint_path
            self._max_src_len = int(self._state.get("config", {}).get("max_src_len", 40))
            self._runtime_loaded = True

    def _describe_rule(self, label: str) -> str:
        if label == "<IDENTITY>":
            return "保留原口令"

        descriptions: list[str] = []
        for op in self._ptn.split_ops(label):
            try:
                code, args = self._ptn.parse_operation(op)
            except Exception:
                descriptions.append(op)
                continue

            if code == "C":
                descriptions.append("首字母大写，其余小写")
            elif code == "U":
                descriptions.append("全部转为大写")
            elif code == "L":
                descriptions.append("全部转为小写")
            elif code == "A":
                descriptions.append(f"末尾追加「{args[0]}」")
            elif code == "P":
                descriptions.append(f"开头添加「{args[0]}」")
            elif code == "DL":
                descriptions.append(f"删除左侧 {args[0]} 个字符")
            elif code == "DR":
                descriptions.append(f"删除右侧 {args[0]} 个字符")
            elif code == "N=":
                descriptions.append(f"将末尾数字替换为「{args[0]}」")
            elif code == "S":
                descriptions.append(f"将「{args[0]}」替换为「{args[1]}」")
            elif code == "I":
                descriptions.append(f"在第 {args[0]} 位插入「{args[1]}」")
            else:
                descriptions.append(op)

        return "，然后".join(descriptions) if descriptions else label

    def predict(
        self,
        password: str,
        *,
        top_k: int,
        beam_size: int,
        label_budget: int,
        decode_len: int,
        constrained: bool,
        include_input: bool,
    ) -> dict[str, Any]:
        self._load_runtime()

        if not self._ptn.is_valid_password(password, max_length=self._max_src_len):
            return {
                "error": (
                    f"Pass2Rule 仅支持 1-{self._max_src_len} 位的可打印 ASCII 口令。"
                ),
                "input_password": password,
                "candidates": [],
                "rules": [],
            }

        started = time.perf_counter()
        search_fn = self._constrained_beam_search if constrained else self._beam_search
        predicted_labels = search_fn(
            self._model,
            password,
            self._max_src_len,
            decode_len,
            beam_size,
            self._device,
            num_return_sequences=label_budget,
            completed_buffer_size=label_budget,
        )

        raw_candidates: list[dict[str, Any]] = []
        if include_input:
            raw_candidates.append(
                {
                    "rank": 0,
                    "password": password,
                    "ptn_rule": "<IDENTITY>",
                    "rule_description": "保留原口令",
                    "score": None,
                }
            )

        for label, score in predicted_labels:
            if not label:
                continue
            try:
                candidate = self._ptn.apply_ptn(password, label)
            except Exception:
                candidate = None
            if candidate is None:
                continue
            raw_candidates.append(
                {
                    "rank": 0,
                    "password": candidate,
                    "ptn_rule": label,
                    "rule_description": self._describe_rule(label),
                    "score": float(score),
                }
            )

        candidates: list[dict[str, Any]] = []
        seen_passwords: set[str] = set()
        for item in raw_candidates:
            candidate_password = item["password"]
            if candidate_password in seen_passwords:
                continue
            seen_passwords.add(candidate_password)
            item = dict(item)
            item["rank"] = len(candidates) + 1
            candidates.append(item)
            if len(candidates) >= top_k:
                break

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "input_password": password,
            "checkpoint": str(self._checkpoint_path),
            "device": str(self._device),
            "latency_ms": elapsed_ms,
            "decode": {
                "constrained": constrained,
                "beam_size": beam_size,
                "label_budget": label_budget,
                "decode_len": decode_len,
                "include_input": include_input,
            },
            "rules": [
                {
                    "rank": item["rank"],
                    "ptn_rule": item["ptn_rule"],
                    "description": item["rule_description"],
                    "score": item["score"],
                }
                for item in candidates
            ],
            "candidates": candidates,
            "count": len(candidates),
        }


_PREDICTOR = _Pass2RulePredictor()


@register_tool("pass2rule")
async def pass2rule_tool(state: PassAgentState) -> dict:
    """使用 PTN Transformer 预测旧口令可能演化出的变体候选。"""
    params = state.get("action_params", {})
    password = str(params.get("password", "") or "")
    if not password:
        return {"_tool_result": {"error": "未提供口令", "candidates": [], "rules": []}}

    top_k = _bounded_int(params.get("top_k"), DEFAULT_TOP_K, 1, MAX_TOP_K)
    beam_size = _bounded_int(params.get("beam_size"), DEFAULT_BEAM_SIZE, 1, MAX_BEAM_SIZE)
    label_budget = _bounded_int(
        params.get("label_budget"),
        DEFAULT_LABEL_BUDGET,
        1,
        MAX_LABEL_BUDGET,
    )
    decode_len = _bounded_int(
        params.get("decode_len"),
        DEFAULT_DECODE_LEN,
        4,
        MAX_DECODE_LEN,
    )
    constrained = _bool_param(params.get("constrained"), True)
    include_input = _bool_param(params.get("include_input"), True)

    try:
        result = await asyncio.to_thread(
            _PREDICTOR.predict,
            password,
            top_k=top_k,
            beam_size=beam_size,
            label_budget=label_budget,
            decode_len=decode_len,
            constrained=constrained,
            include_input=include_input,
        )
    except Exception as exc:
        result = {
            "input_password": password,
            "error": str(exc),
            "candidates": [],
            "rules": [],
            "model_dir": os.path.abspath(PASS2RULE_MODEL_DIR),
            "checkpoint": os.path.abspath(PASS2RULE_CHECKPOINT_PATH),
            "device": PASS2RULE_DEVICE,
        }

    return {"_tool_result": result}
