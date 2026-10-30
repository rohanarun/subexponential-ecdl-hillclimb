#!/usr/bin/env python3
"""Validate CLAIMS.md against the committed evidence.

This is the anti-overclaim gate. It does not judge mathematics; it checks that
each status is backed by the kind of artifact the status promises, and that
conditional claims only depend on claims that exist.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "CLAIMS.md"
AXIOMS = ROOT / "AXIOMS.md"

STATUSES = {
    "proved",
    "tested",
    "implemented",
    "conditional",
    "assumed",
    "open",
    "refuted",
    "not-claimed",
}

REQUIRED_COLUMNS = ("ID", "Claim", "Status", "Depends on", "Evidence")


class ClaimError(ValueError):
    pass


def parse_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header_seen = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not header_seen:
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if tuple(cells) == REQUIRED_COLUMNS:
                header_seen = True
            continue
        if not stripped.startswith("|"):
            break
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(REQUIRED_COLUMNS):
            raise ClaimError(f"line {line_number}: expected 5 cells, got {len(cells)}")
        rows.append(dict(zip(REQUIRED_COLUMNS, cells)))
    if not header_seen:
        raise ClaimError("no claim table header found")
    if not rows:
        raise ClaimError("claim table is empty")
    return rows


def split_list(value: str) -> list[str]:
    value = value.strip()
    if value in {"", "—", "-", "none", "None"}:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def split_dependencies(value: str) -> list[str]:
    value = value.strip()
    if value in {"", "—", "-", "none", "None"}:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def resolve_evidence(item: str) -> Path:
    path_part = item.split("#", 1)[0].strip()
    if not path_part:
        raise ClaimError(f"empty evidence path in {item!r}")
    path = (ROOT / path_part).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ClaimError(f"evidence escapes the repository: {item!r}")
    if not path.exists():
        raise ClaimError(f"evidence path does not exist: {path_part}")
    return path


def check_evidence(claim_id: str, status: str, evidence: list[str], axioms_text: str) -> None:
    if status in {"open", "not-claimed", "conditional"}:
        return
    if not evidence:
        raise ClaimError(f"{claim_id}: status {status!r} requires evidence")

    paths = [resolve_evidence(item) for item in evidence]

    if status == "assumed":
        if not any(path.name == "AXIOMS.md" for path in paths):
            raise ClaimError(f"{claim_id}: assumed claims must point at AXIOMS.md")
        if "#a1" not in " ".join(item.lower() for item in evidence):
            raise ClaimError(f"{claim_id}: assumed claims must point at AXIOMS.md#a1")
        if "## A1" not in axioms_text:
            raise ClaimError("AXIOMS.md is missing the A1 anchor")

    if status == "proved":
        lean_files = [path for path in paths if path.suffix == ".lean"]
        if not lean_files:
            raise ClaimError(f"{claim_id}: proved claims require a .lean file")
        for path in lean_files:
            if re.search(r"\bsorry\b", path.read_text(encoding="utf-8")):
                raise ClaimError(f"{claim_id}: {path.name} contains 'sorry'")

    if status == "tested":
        has_test = any("tests" in path.parts for path in paths)
        has_source = any("src" in path.parts or "lean" in path.parts for path in paths)
        if not has_test:
            raise ClaimError(f"{claim_id}: tested claims require a test path")
        if not has_source:
            raise ClaimError(f"{claim_id}: tested claims require a source path")

    if status == "implemented":
        if not any("src" in path.parts or "lean" in path.parts for path in paths):
            raise ClaimError(f"{claim_id}: implemented claims require a source path")

    if status == "refuted":
        if not paths:
            raise ClaimError(f"{claim_id}: refuted claims require a counterexample path")


def main() -> int:
    try:
        text = CLAIMS.read_text(encoding="utf-8")
        axioms_text = AXIOMS.read_text(encoding="utf-8")
        rows = parse_rows(text)
    except (OSError, ClaimError) as error:
        print(f"claim graph error: {error}", file=sys.stderr)
        return 1

    by_id: dict[str, dict[str, str]] = {}
    errors: list[str] = []

    for row in rows:
        claim_id = row["ID"]
        if not re.fullmatch(r"[A-Z][0-9]+", claim_id):
            errors.append(f"{claim_id}: ID must match [A-Z][0-9]+")
        if claim_id in by_id:
            errors.append(f"{claim_id}: duplicate ID")
        by_id[claim_id] = row
        status = row["Status"]
        if status not in STATUSES:
            errors.append(f"{claim_id}: unknown status {status!r}")

    for row in rows:
        claim_id = row["ID"]
        status = row["Status"]
        dependencies = split_dependencies(row["Depends on"])
        evidence = split_list(row["Evidence"])

        if claim_id in dependencies:
            errors.append(f"{claim_id}: depends on itself")
        for dependency in dependencies:
            if dependency not in by_id:
                errors.append(f"{claim_id}: unknown dependency {dependency!r}")
                continue
            dependency_status = by_id[dependency]["Status"]
            if dependency_status in {"refuted", "not-claimed"}:
                errors.append(
                    f"{claim_id}: depends on {dependency} whose status is {dependency_status!r}"
                )

        if status == "conditional" and not dependencies:
            errors.append(f"{claim_id}: conditional claims require dependencies")

        try:
            check_evidence(claim_id, status, evidence, axioms_text)
        except (ClaimError, OSError) as error:
            errors.append(str(error))

    if errors:
        for error in errors:
            print(f"claim graph error: {error}", file=sys.stderr)
        return 1

    counts = Counter(row["Status"] for row in rows)
    summary = ", ".join(f"{status}={counts[status]}" for status in sorted(counts))
    print(f"claim graph ok: {len(rows)} claims ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
