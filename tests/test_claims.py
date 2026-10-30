import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_claim_graph_passes_its_own_gate():
    result = subprocess.run(
        [sys.executable, str(ROOT / "eval" / "verify_claims.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "claim graph ok" in result.stdout.lower()
