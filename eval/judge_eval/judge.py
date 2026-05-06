import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).parent
EVAL_DIR = ROOT_DIR.parent

PROMPT_FILE = ROOT_DIR / "LLMjudge.prompt"
DEFAULT_INPUT = EVAL_DIR / "data" / "test_cases.json"
DEFAULT_OUTPUT = ROOT_DIR / "results.json"


def build_prompt(template: str, case: dict) -> str:
    return template.format(
        user_prompt=case["user_prompt"],
        user_profile_summary=case.get("user_profile_summary", ""),
        assistant_final_answer=case["assistant_final_answer"],
    )


def call_judge(client: OpenAI, model: str, prompt: str, max_retries: int, max_tokens: int) -> str:
    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=max_tokens,
                timeout=300,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            if attempt >= max_retries:
                raise
            err = sys.exc_info()[1]
            wait_seconds = min(2**attempt, 30)
            if err and (
                "RateLimit" in err.__class__.__name__
                or "429" in str(err)
                or "请求数限制" in str(err)
            ):
                wait_seconds = 310
            print(f"judge request failed, retrying in {wait_seconds}s: {err}", flush=True)
            time.sleep(wait_seconds)
    raise RuntimeError("judge request failed")


def parse_response(raw: str) -> dict:
    result = {"raw": raw, "analysis": "", "A": None, "B": None, "C": None}

    m = re.search(r"Analysis:\s*(.+?)(?=\n[ABC]:)", raw, re.DOTALL)
    if m:
        result["analysis"] = m.group(1).strip()

    for dim in ("A", "B", "C"):
        m = re.search(rf"{dim}:\s*(\d)\s*\|\s*(.+)", raw)
        if m:
            result[dim] = {
                "score": int(m.group(1)),
                "reason": m.group(2).strip(),
            }

    return result


def normalize_dimension(value) -> dict | None:
    if isinstance(value, dict):
        try:
            score = int(value.get("score"))
        except (TypeError, ValueError):
            return None
        return {"score": score, "reason": str(value.get("reason", "")).strip()}
    if isinstance(value, str):
        m = re.search(r"(\d)\s*\|\s*(.+)", value)
        if m:
            return {"score": int(m.group(1)), "reason": m.group(2).strip()}
    return None


def parse_batch_response(raw: str) -> dict[str, dict]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("batch judge response did not contain a JSON array")
    data = json.loads(cleaned[start : end + 1])
    parsed = {}
    for item in data:
        case_id = str(item.get("id", "")).strip()
        if not case_id:
            continue
        parsed[case_id] = {
            "raw": json.dumps(item, ensure_ascii=False),
            "analysis": str(item.get("analysis", "")).strip(),
            "A": normalize_dimension(item.get("A")),
            "B": normalize_dimension(item.get("B")),
            "C": normalize_dimension(item.get("C")),
        }
    return parsed


def compute_total(parsed: dict) -> float | None:
    a = parsed.get("A")
    b = parsed.get("B")
    c = parsed.get("C")
    if not all([a, b, c]):
        return None
    if b["score"] < 3:
        return 0.0
    return round(0.4 * a["score"] + 0.3 * b["score"] + 0.3 * c["score"], 2)


def build_result_entry(case: dict, case_id: str, target_model: str | None, judge_model: str, raw: str) -> dict:
    parsed = parse_response(raw)
    return build_result_entry_from_parsed(case, case_id, target_model, judge_model, parsed)


def build_result_entry_from_parsed(
    case: dict,
    case_id: str,
    target_model: str | None,
    judge_model: str,
    parsed: dict,
) -> dict:
    total = compute_total(parsed)
    return {
        "id": case_id,
        "category": case.get("category"),
        "target_model": target_model,
        "judge_model": judge_model,
        "scores": {
            "A": parsed["A"],
            "B": parsed["B"],
            "C": parsed["C"],
        },
        "total": total,
        "analysis": parsed["analysis"],
        "raw_response": parsed["raw"],
    }


def status_line(entry: dict) -> str:
    scores = entry["scores"]
    return (
        f"  A={scores['A']['score'] if scores['A'] else '?'}"
        f"  B={scores['B']['score'] if scores['B'] else '?'}"
        f"  C={scores['C']['score'] if scores['C'] else '?'}"
        f"  Total={entry['total']}"
    )


def build_batch_prompt(template: str, cases: list[tuple[int, dict]]) -> str:
    if "===== 评分标准 =====" in template:
        rubric = template.split("===== 评分标准 =====", 1)[1]
        rubric = rubric.split("===== 输出格式 =====", 1)[0]
        rubric = "===== 评分标准 =====" + rubric
    else:
        rubric = template

    case_blocks = []
    for index, case in cases:
        case_id = case.get("id", f"case_{index}")
        case_blocks.append(
            "\n".join(
                [
                    f"===== 案例 {case_id} =====",
                    "【用户输入】",
                    str(case["user_prompt"]),
                    "",
                    "【用户画像摘要】",
                    str(case.get("user_profile_summary", "")),
                    "",
                    "【系统回复】",
                    str(case["assistant_final_answer"]),
                ]
            )
        )

    return f"""你是一个口令安全助手系统的评审专家。请严格根据同一套评分标准，对以下多个案例分别独立打分。

{rubric}

===== 待评审案例 =====

{chr(10).join(case_blocks)}

===== 输出要求 =====

只输出一个 JSON 数组，不要输出 Markdown，不要加代码块。数组中每个对象必须对应一个案例，格式如下：
[
  {{
    "id": "JP-0001",
    "analysis": "2-4 句话简要分析",
    "A": {{"score": 0, "reason": "一句话理由"}},
    "B": {{"score": 0, "reason": "一句话理由"}},
    "C": {{"score": 0, "reason": "一句话理由"}}
  }}
]
"""


def load_cases(input_file: Path) -> list[dict]:
    text = input_file.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if input_file.suffix == ".jsonl" or not stripped.startswith("["):
        cases = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{input_file}:{line_no} is not valid JSONL") from exc
        return cases
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(f"{input_file} must contain a JSON array or JSONL records")
    return data


def case_for_model(case: dict, target_model: str | None) -> dict | None:
    if target_model:
        outputs = case.get("model_outputs")
        if not isinstance(outputs, dict) or target_model not in outputs:
            return None
        selected = dict(case)
        selected["assistant_final_answer"] = outputs[target_model]
        return selected
    if "assistant_final_answer" in case:
        return dict(case)
    return None


def load_completed_ids(output_file: Path) -> set[str]:
    if not output_file.exists():
        return set()
    if output_file.suffix == ".jsonl":
        completed = set()
        for line in output_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in entry:
                completed.add(str(entry["id"]))
        return completed
    try:
        data = json.loads(output_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {str(entry["id"]) for entry in data.get("results", []) if "id" in entry}


def write_result(output_file: Path, entry: dict, append_jsonl: bool) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if append_jsonl:
        with output_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run LLM-as-judge evaluation.")
    parser.add_argument("input_file", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("output_file", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--target-model",
        help="Select this key from each case's model_outputs field.",
    )
    parser.add_argument(
        "--judge-model",
        default=os.environ.get("MODEL", "claude-opus-4-6"),
        help="Judge model name. Defaults to MODEL in .env.",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    return parser


def main():
    load_dotenv(ROOT_DIR / ".env")
    args = build_arg_parser().parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("BASE_URL", "")
    model = args.judge_model

    if not api_key:
        print("请在 .env 文件中设置 OPENAI_API_KEY")
        sys.exit(1)

    input_file = args.input_file
    output_file = args.output_file

    client = OpenAI(base_url=base_url, api_key=api_key)
    template = PROMPT_FILE.read_text(encoding="utf-8")

    raw_cases = load_cases(input_file)
    cases = []
    skipped_missing_model = 0
    for case in raw_cases:
        selected = case_for_model(case, args.target_model)
        if selected is None:
            skipped_missing_model += 1
            continue
        cases.append(selected)
    if args.limit:
        cases = cases[: args.limit]

    completed_ids = load_completed_ids(output_file) if args.resume else set()
    append_jsonl = output_file.suffix == ".jsonl"
    results = []
    if not append_jsonl:
        output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    print(f"评审模型: {model}")
    if args.target_model:
        print(f"被评模型: {args.target_model}")
    print(f"待评条数: {len(cases)}")
    if skipped_missing_model:
        print(f"跳过缺少目标模型输出的条数: {skipped_missing_model}")
    if completed_ids:
        print(f"断点续跑，已完成条数: {len(completed_ids)}")

    pending_cases = []
    for i, case in enumerate(cases):
        case_id = case.get("id", f"case_{i}")
        if str(case_id) in completed_ids:
            print(f"[{i+1}/{len(cases)}] 跳过已完成 {case_id}")
            continue
        pending_cases.append((i, case))

    def evaluate_case(index: int, case: dict) -> dict:
        case_id = str(case.get("id", f"case_{index}"))
        prompt = build_prompt(template, case)
        raw = call_judge(client, model, prompt, args.max_retries, args.max_tokens)
        return build_result_entry(case, case_id, args.target_model, model, raw)

    def evaluate_batch(batch: list[tuple[int, dict]]) -> list[tuple[int, dict]]:
        prompt = build_batch_prompt(template, batch)
        raw = call_judge(client, model, prompt, args.max_retries, args.max_tokens)
        parsed_by_id = parse_batch_response(raw)
        entries = []
        for index, case in batch:
            case_id = str(case.get("id", f"case_{index}"))
            parsed = parsed_by_id.get(case_id)
            if not parsed:
                raise ValueError(f"batch judge response missing case {case_id}")
            entry = build_result_entry_from_parsed(case, case_id, args.target_model, model, parsed)
            entries.append((index, entry))
        return entries

    def record_result(index: int, entry: dict) -> None:
        results.append(entry)
        write_result(output_file, entry, append_jsonl)
        print(f"[{index+1}/{len(cases)}] 完成 {entry['id']}")
        print(status_line(entry))

    if args.batch_size > 1 and args.workers > 1:
        raise ValueError("--batch-size > 1 cannot be combined with --workers > 1")

    if args.batch_size > 1:
        for offset in range(0, len(pending_cases), args.batch_size):
            batch = pending_cases[offset : offset + args.batch_size]
            first_id = batch[0][1].get("id", f"case_{batch[0][0]}")
            last_id = batch[-1][1].get("id", f"case_{batch[-1][0]}")
            print(f"[{batch[0][0]+1}-{batch[-1][0]+1}/{len(cases)}] 批量评审 {first_id}..{last_id}")
            for index, entry in evaluate_batch(batch):
                record_result(index, entry)
            if offset + args.batch_size < len(pending_cases):
                time.sleep(args.sleep)
    elif args.workers <= 1:
        for i, case in pending_cases:
            case_id = case.get("id", f"case_{i}")
            print(f"[{i+1}/{len(cases)}] 评审 {case_id} ...")
            entry = evaluate_case(i, case)
            record_result(i, entry)
            if i < len(cases) - 1:
                time.sleep(args.sleep)
    else:
        print(f"并发 worker 数: {args.workers}")
        pending_iter = iter(pending_cases)
        futures = {}
        submitted = 0

        def submit_next(executor: ThreadPoolExecutor) -> bool:
            nonlocal submitted
            try:
                index, case = next(pending_iter)
            except StopIteration:
                return False
            case_id = case.get("id", f"case_{index}")
            print(f"[{index+1}/{len(cases)}] 提交 {case_id}")
            futures[executor.submit(evaluate_case, index, case)] = index
            submitted += 1
            if args.sleep:
                time.sleep(args.sleep)
            return True

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            while len(futures) < args.workers and submit_next(executor):
                pass
            while futures:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    index = futures.pop(future)
                    entry = future.result()
                    record_result(index, entry)
                    submit_next(executor)

    if not append_jsonl:
        output = {
            "judge_model": model,
            "target_model": args.target_model,
            "input_file": str(input_file),
            "total_cases": len(results),
            "skipped_missing_model": skipped_missing_model,
            "results": results,
        }

        output_file.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(f"\n完成，结果已写入 {output_file}")


if __name__ == "__main__":
    main()
