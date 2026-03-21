"""passgpt_prob 工具：使用 PassGPT ONNX 模型评估口令被猜中的概率。"""
from __future__ import annotations

import math
import os
import threading
import time
from typing import Any

from agent.graph import register_tool
from agent.state import PassAgentState
from config import PASSGPT_MODEL_PATH

_CLS_TOKEN_ID = 2
_UNK_TOKEN = "[UNK]"
_CHARS = [
    "[UNK]", "[SEP]", "[CLS]", "[PAD]", "[MASK]",
    " ", "!", '"', "#", "$",
    "%", "&", "'", "(", ")",
    "*", "+", ",", "-", ".",
    "/", "0", "1", "2", "3",
    "4", "5", "6", "7", "8",
    "9", ":", ";", "<", "=",
    ">", "?", "@", "A", "B",
    "C", "D", "E", "F", "G",
    "H", "I", "J", "K", "L",
    "M", "N", "O", "P", "Q",
    "R", "S", "T", "U", "V",
    "W", "X", "Y", "Z", "[",
    "\\", "]", "^", "_", "`",
    "a", "b", "c", "d", "e",
    "f", "g", "h", "i", "j",
    "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t",
    "u", "v", "w", "x", "y",
    "z", "{", "|", "}", "~",
]
_CHAR_TO_INDEX = {char: idx for idx, char in enumerate(_CHARS)}
_UNK_INDEX = _CHAR_TO_INDEX[_UNK_TOKEN]


def _require_modules() -> tuple[Any, Any]:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "缺少 numpy 依赖，请在 backend 目录执行 `uv sync` 安装依赖。"
        ) from exc

    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError(
            "缺少 onnxruntime 依赖，请在 backend 目录执行 `uv sync` 安装依赖。"
        ) from exc

    return np, ort

def _softmax(logits: Any, np: Any) -> Any:
    shifted = logits - np.max(logits)
    exp_logits = np.exp(shifted)
    return exp_logits / np.sum(exp_logits)


def _password_to_tensor(password: str, prefix_len: int, np: Any) -> Any:
    token_ids = [_CLS_TOKEN_ID]
    token_ids.extend(_CHAR_TO_INDEX.get(ch, _UNK_INDEX) for ch in password[:prefix_len])
    return np.asarray([token_ids], dtype=np.int64)


def _next_char_probability(raw_output: Any, next_char: str, np: Any) -> float:
    logits = np.asarray(raw_output).reshape(-1)[-len(_CHARS):]
    probs = _softmax(logits, np)
    next_index = _CHAR_TO_INDEX.get(next_char, _UNK_INDEX)
    return float(probs[next_index])


def _estimate_guesses(log_prob: float) -> tuple[float, int | None]:
    guesses_log10 = max(0.0, -log_prob / math.log(10))
    if guesses_log10 > 18:
        return guesses_log10, None
    return guesses_log10, max(1, int(round(math.exp(-log_prob))))


class _PassGPTScorer:
    def __init__(self) -> None:
        self._session = None
        self._input_name = ""
        self._providers: list[str] = []
        self._lock = threading.Lock()

    def _ensure_session(self) -> tuple[Any, Any]:
        np, ort = _require_modules()

        if self._session is not None:
            return np, self._session

        with self._lock:
            if self._session is not None:
                return np, self._session

            if not os.path.exists(PASSGPT_MODEL_PATH):
                raise RuntimeError(f"PassGPT 模型文件不存在: {PASSGPT_MODEL_PATH}")

            providers = ["CPUExecutionProvider"]
            session = ort.InferenceSession(PASSGPT_MODEL_PATH, providers=providers)
            self._session = session
            self._input_name = session.get_inputs()[0].name
            self._providers = session.get_providers()

        return np, self._session

    def score(self, password: str) -> dict[str, Any]:
        np, session = self._ensure_session()

        if password == "":
            return {
                "password_length": 0,
                "probability": 1.0,
                "log_probability": 0.0,
                "guesses_log10_estimate": 0.0,
                "guesses_estimate": 1,
                "char_probabilities": [],
                "backend": self._providers,
                "model_path": PASSGPT_MODEL_PATH,
                "guess_estimate_method": "inverse_probability",
                "latency_ms": 0.0,
            }

        started = time.perf_counter()
        char_probs: list[float] = []
        log_prob = 0.0

        for idx, next_char in enumerate(password):
            input_tensor = _password_to_tensor(password, idx, np)
            raw_output = session.run(None, {self._input_name: input_tensor})[0]
            next_prob = _next_char_probability(raw_output, next_char, np)
            next_prob = max(next_prob, 1e-300)
            char_probs.append(next_prob)
            log_prob += math.log(next_prob)

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        probability = 0.0 if log_prob < math.log(1e-300) else float(math.exp(log_prob))
        guesses_log10, guesses_estimate = _estimate_guesses(log_prob)

        return {
            "password_length": len(password),
            "probability": probability,
            "log_probability": round(log_prob, 6),
            "guesses_log10_estimate": round(guesses_log10, 6),
            "guesses_estimate": guesses_estimate,
            "char_probabilities": char_probs,
            "backend": self._providers,
            "model_path": PASSGPT_MODEL_PATH,
            "guess_estimate_method": "inverse_probability",
            "latency_ms": elapsed_ms,
        }


_SCORER = _PassGPTScorer()


@register_tool("passgpt_prob")
async def passgpt_prob_tool(state: PassAgentState) -> dict:
    """使用 PassGPT ONNX 模型评估口令被猜中的概率。"""
    params = state.get("action_params", {})
    password = params.get("password", "")

    result = _SCORER.score(password)
    return {"_tool_result": result}
