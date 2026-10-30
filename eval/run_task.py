#!/usr/bin/env python3
"""Run one auto-research task and record its verifier output.

Usage:
    python3.12 eval/run_task.py tasks/T01-btn-core.yaml
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "eval" / "results"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path, help="path to a task YAML file")
    parser.add_argument("--timeout", type=int, default=900, help="verifier timeout in seconds")
    args = parser.parse_args()

    task_path = args.task if args.task.is_absolute() else (ROOT / args.task)
    if not task_path.exists():
        print(f"task not found: {task_path}", file=sys.stderr)
        return 2

    task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    if not isinstance(task, dict):
        print("task file must contain a mapping", file=sys.stderr)
        return 2
    for field in ("id", "claim", "title", "verifier"):
        if field not in task:
            print(f"task is missing required field {field!r}", file=sys.stderr)
            return 2

    try:
        completed = subprocess.run(
            task["verifier"],
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        timed_out = False
    except subprocess.TimeoutExpired as error:
        completed = subprocess.CompletedProcess(
            args=task["verifier"],
            returncode=124,
            stdout=(error.stdout or ""),
            stderr=(error.stderr or ""),
        )
        timed_out = True

    RESULTS.mkdir(parents=True, exist_ok=True)
    record = {
        "task_id": task["id"],
        "claim": task["claim"],
        "title": task["title"],
        "status": task.get("status", "open"),
        "verifier": task["verifier"],
        "returncode": completed.returncode,
        "timed_out": timed_out,
        "passed": completed.returncode == 0,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stdout_tail": (completed.stdout or "")[-4000:],
        "stderr_tail": (completed.stderr or "")[-4000:],
    }
    output = RESULTS / f"{task['id']}.json"
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"{task['id']}: {'PASS' if record['passed'] else 'FAIL'} (exit {completed.returncode})")
    print(f"record: {output.relative_to(ROOT)}")
    if not record["passed"]:
        if record["stdout_tail"]:
            print("--- stdout ---")
            print(record["stdout_tail"])
        if record["stderr_tail"]:
            print("--- stderr ---")
            print(record["stderr_tail"])
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
