import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

PROMPT_FILE = "LLMjudge.prompt"
DEFAULT_INPUT = "data/test_cases.json"
DEFAULT_OUTPUT = "results.json"


def load_prompt_template() -> str:
    path = Path(__file__).parent / PROMPT_FILE
    return path.read_text(encoding="utf-8")


def build_prompt(template: str, case: dict) -> str:
    return template.format(
        user_prompt=case["user_prompt"],
        user_profile_summary=case.get("user_profile_summary", ""),
        assistant_final_answer=case["assistant_final_answer"],
    )


def call_judge(client: OpenAI, model: str, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1024,
    )
    return resp.choices[0].message.content.strip()


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


def compute_total(parsed: dict) -> float | None:
    a = parsed.get("A")
    b = parsed.get("B")
    c = parsed.get("C")
    if not all([a, b, c]):
        return None
    if b["score"] < 3:
        return 0.0
    return round(0.4 * a["score"] + 0.3 * b["score"] + 0.3 * c["score"], 2)


def main():
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("BASE_URL", "")
    model = os.environ.get("MODEL", "claude-opus-4-6")

    if not api_key:
        print("请在 .env 文件中设置 OPENAI_API_KEY")
        sys.exit(1)

    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    client = OpenAI(base_url=base_url, api_key=api_key)
    template = load_prompt_template()

    cases = json.loads(Path(input_file).read_text(encoding="utf-8"))
    results = []

    for i, case in enumerate(cases):
        case_id = case.get("id", f"case_{i}")
        print(f"[{i+1}/{len(cases)}] 评审 {case_id} ...")

        prompt = build_prompt(template, case)
        raw = call_judge(client, model, prompt)
        parsed = parse_response(raw)
        total = compute_total(parsed)

        entry = {
            "id": case_id,
            "scores": {
                "A": parsed["A"],
                "B": parsed["B"],
                "C": parsed["C"],
            },
            "total": total,
            "analysis": parsed["analysis"],
            "raw_response": parsed["raw"],
        }
        results.append(entry)

        status = f"  A={parsed['A']['score'] if parsed['A'] else '?'}"
        status += f"  B={parsed['B']['score'] if parsed['B'] else '?'}"
        status += f"  C={parsed['C']['score'] if parsed['C'] else '?'}"
        status += f"  Total={total}"
        print(status)

        if i < len(cases) - 1:
            time.sleep(1)

    output = {
        "model": model,
        "total_cases": len(results),
        "results": results,
    }

    Path(output_file).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n完成，结果已写入 {output_file}")


if __name__ == "__main__":
    main()