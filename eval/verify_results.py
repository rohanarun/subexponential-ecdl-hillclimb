#!/usr/bin/env python3
"""Validate committed research results under auto-research/.

This is a format and evidence gate, not a mathematical judge. It checks that
each result folder has the required write-up and metadata, that paths stay
inside the folder, and that the outcome vocabulary is respected.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "auto-research"

TRACKS = {"encodings", "coverage", "lean", "d1-audit", "reproduction", "other"}
OUTCOMES = {"positive", "negative", "inconclusive", "reproduced", "refuted"}
RECOMMENDATIONS = {"no-change", "promote-tested", "promote-proved", "refute"}

REQUIRED_FIELDS = {
    "run_id",
    "agent",
    "date",
    "track",
    "task",
    "claim",
    "outcome",
    "summary",
    "commands",
    "environment",
    "artifacts",
    "claim_status_recommendation",
    "notes",
}


def fail(message: str) -> None:
    raise ValueError(message)


def check_result(result_dir: Path) -> None:
    readme = result_dir / "README.md"
    metadata = result_dir / "result.json"

    if not readme.exists():
        fail(f"{result_dir.name}: missing README.md")
    if not readme.read_text(encoding="utf-8").strip():
        fail(f"{result_dir.name}: README.md is empty")
    if not metadata.exists():
        fail(f"{result_dir.name}: missing result.json")

    try:
        result = json.loads(metadata.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"{result_dir.name}: result.json is not valid JSON: {error}")

    if not isinstance(result, dict):
        fail(f"{result_dir.name}: result.json must contain an object")

    missing = REQUIRED_FIELDS - set(result)
    if missing:
        fail(f"{result_dir.name}: missing fields {sorted(missing)}")

    run_id = result["run_id"]
    if run_id != result_dir.name:
        fail(f"{result_dir.name}: run_id must equal the folder name")

    date = result["date"]
    try:
        parsed_date = dt.date.fromisoformat(date)
    except (TypeError, ValueError):
        fail(f"{result_dir.name}: date must be YYYY-MM-DD")
    if not run_id.startswith(f"{parsed_date.isoformat()}-"):
        fail(f"{result_dir.name}: run_id must start with the date")

    track = result["track"]
    if track not in TRACKS:
        fail(f"{result_dir.name}: unknown track {track!r}")
    if result_dir.parent.name != track:
        fail(f"{result_dir.name}: track {track!r} does not match parent folder {result_dir.parent.name!r}")

    if not re.fullmatch(r"T\d+", str(result["task"])):
        fail(f"{result_dir.name}: task must look like T01")
    if not re.fullmatch(r"[A-Z]\d+", str(result["claim"])):
        fail(f"{result_dir.name}: claim must look like C5")

    outcome = result["outcome"]
    if outcome not in OUTCOMES:
        fail(f"{result_dir.name}: unknown outcome {outcome!r}")

    recommendation = result["claim_status_recommendation"]
    if recommendation not in RECOMMENDATIONS:
        fail(f"{result_dir.name}: unknown claim_status_recommendation {recommendation!r}")
    if outcome == "refuted" and recommendation != "refute":
        fail(f"{result_dir.name}: a refuted outcome must recommend 'refute'")
    if outcome != "refuted" and recommendation == "refute":
        fail(f"{result_dir.name}: only a refuted outcome may recommend 'refute'")

    if not isinstance(result["agent"], str) or not result["agent"].strip():
        fail(f"{result_dir.name}: agent must be a non-empty string")
    if not isinstance(result["environment"], str) or not result["environment"].strip():
        fail(f"{result_dir.name}: environment must be a non-empty string")
    if not isinstance(result["summary"], str) or not result["summary"].strip():
        fail(f"{result_dir.name}: summary must be a non-empty string")
    if len(result["summary"]) > 2000:
        fail(f"{result_dir.name}: summary is too long")
    if not isinstance(result["notes"], str):
        fail(f"{result_dir.name}: notes must be a string")

    commands = result["commands"]
    if not isinstance(commands, list) or not commands:
        fail(f"{result_dir.name}: commands must be a non-empty list")
    if not all(isinstance(command, str) and command.strip() for command in commands):
        fail(f"{result_dir.name}: every command must be a non-empty string")

    artifacts = result["artifacts"]
    if not isinstance(artifacts, list):
        fail(f"{result_dir.name}: artifacts must be a list")
    for artifact in artifacts:
        if not isinstance(artifact, str) or not artifact.strip():
            fail(f"{result_dir.name}: artifact paths must be non-empty strings")
        artifact_path = Path(artifact)
        if artifact_path.is_absolute() or ".." in artifact_path.parts:
            fail(f"{result_dir.name}: artifact path must stay inside the result folder: {artifact!r}")
        resolved = (result_dir / artifact_path).resolve()
        if result_dir.resolve() not in resolved.parents:
            fail(f"{result_dir.name}: artifact path escapes the result folder: {artifact!r}")
        if not resolved.exists():
            fail(f"{result_dir.name}: artifact does not exist: {artifact!r}")


def iter_result_dirs() -> list[Path]:
    """Return ``auto-research/<track>/<run_id>/`` directories.

    The track level is structural, not a result.  A result placed directly in
    ``auto-research/`` is rejected instead of being silently treated as a track.
    """
    if not RESULTS.exists():
        return []

    errors: list[str] = []
    result_dirs: list[Path] = []
    for track_dir in sorted(RESULTS.iterdir()):
        if not track_dir.is_dir() or track_dir.name == "_template":
            continue
        if track_dir.name not in TRACKS:
            errors.append(
                f"{track_dir.name}: unknown track folder; expected one of {sorted(TRACKS)}"
            )
            continue
        for result_dir in sorted(track_dir.iterdir()):
            if result_dir.is_dir():
                result_dirs.append(result_dir)
    if errors:
        raise ValueError("; ".join(errors))
    return result_dirs


def main() -> int:
    try:
        result_dirs = iter_result_dirs()
    except (OSError, ValueError) as error:
        print(f"auto-research error: {error}", file=sys.stderr)
        return 1

    if not result_dirs:
        print("auto-research results ok: 0 result(s)")
        return 0

    errors: list[str] = []
    for result_dir in result_dirs:
        try:
            check_result(result_dir)
        except (OSError, ValueError) as error:
            errors.append(str(error))

    if errors:
        for error in errors:
            print(f"auto-research error: {error}", file=sys.stderr)
        return 1

    print(f"auto-research results ok: {len(result_dirs)} result(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
