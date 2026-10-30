import json
import subprocess
import sys
from pathlib import Path

import pytest

from eval import verify_results

ROOT = Path(__file__).resolve().parents[1]

VALID_RESULT = {
    "run_id": "2026-10-30-T01-smoke",
    "agent": "test-agent",
    "date": "2026-10-30",
    "track": "reproduction",
    "task": "T01",
    "claim": "C1",
    "outcome": "reproduced",
    "summary": "The toy BTN tests pass on a clean checkout.",
    "commands": ["python -m pytest tests/test_network.py -q"],
    "environment": "Python 3.12, test",
    "artifacts": [],
    "claim_status_recommendation": "no-change",
    "notes": "Bounded check only.",
}


def make_result(root: Path, metadata: dict | None = None, name: str | None = None) -> Path:
    run_id = (metadata or VALID_RESULT)["run_id"]
    folder = root / "auto-research" / "reproduction" / (name or run_id)
    folder.mkdir(parents=True)
    (folder / "README.md").write_text("# result\n", encoding="utf-8")
    (folder / "result.json").write_text(
        json.dumps(metadata or VALID_RESULT), encoding="utf-8"
    )
    return folder


def test_auto_research_results_pass_their_gate():
    result = subprocess.run(
        [sys.executable, str(ROOT / "eval" / "verify_results.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "auto-research results ok" in result.stdout


def test_valid_result_folder_passes(tmp_path):
    folder = make_result(tmp_path)
    verify_results.check_result(folder)


def test_run_id_must_match_folder_name(tmp_path):
    folder = make_result(tmp_path, name="different-folder")
    with pytest.raises(ValueError, match="run_id must equal the folder name"):
        verify_results.check_result(folder)


def test_unknown_outcome_is_rejected(tmp_path):
    folder = make_result(tmp_path, {**VALID_RESULT, "outcome": "success"})
    with pytest.raises(ValueError, match="unknown outcome"):
        verify_results.check_result(folder)


def test_refuted_outcome_requires_refute_recommendation(tmp_path):
    folder = make_result(tmp_path, {**VALID_RESULT, "outcome": "refuted"})
    with pytest.raises(ValueError, match="must recommend 'refute'"):
        verify_results.check_result(folder)


def test_refute_recommendation_requires_refuted_outcome(tmp_path):
    folder = make_result(
        tmp_path, {**VALID_RESULT, "claim_status_recommendation": "refute"}
    )
    with pytest.raises(ValueError, match="only a refuted outcome"):
        verify_results.check_result(folder)


def test_artifact_must_stay_inside_the_result_folder(tmp_path):
    folder = make_result(tmp_path, {**VALID_RESULT, "artifacts": ["../outside.log"]})
    with pytest.raises(ValueError, match="must stay inside"):
        verify_results.check_result(folder)


def test_missing_artifact_is_rejected(tmp_path):
    folder = make_result(tmp_path, {**VALID_RESULT, "artifacts": ["artifacts/missing.log"]})
    with pytest.raises(ValueError, match="artifact does not exist"):
        verify_results.check_result(folder)


def test_track_must_match_parent_folder(tmp_path):
    folder = make_result(tmp_path, {**VALID_RESULT, "track": "coverage"})
    with pytest.raises(ValueError, match="does not match parent folder"):
        verify_results.check_result(folder)


def test_iter_result_dirs_finds_nested_runs(tmp_path, monkeypatch):
    make_result(tmp_path)
    monkeypatch.setattr(verify_results, "RESULTS", tmp_path / "auto-research")
    assert [path.name for path in verify_results.iter_result_dirs()] == [
        VALID_RESULT["run_id"]
    ]


def test_iter_result_dirs_rejects_unknown_track(tmp_path, monkeypatch):
    (tmp_path / "auto-research" / "misc").mkdir(parents=True)
    monkeypatch.setattr(verify_results, "RESULTS", tmp_path / "auto-research")
    with pytest.raises(ValueError, match="unknown track folder"):
        verify_results.iter_result_dirs()
