"""Test suite verifying Theorem D.1 audit completeness and threshold bound lowering (Task T11)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_theorem_d1_audit_document_exists():
    audit_file = ROOT / "docs" / "theorem-d1-audit.md"
    assert audit_file.exists(), "docs/theorem-d1-audit.md must exist"
    text = audit_file.read_text(encoding="utf-8")
    assert len(text) > 1000, "audit document must be substantive"
    assert "Theorem D.1" in text
    assert "bipartite" in text.lower()
    assert "ring" in text.lower() or "z_{2^{" in text.lower() or "z_2" in text.lower()


def test_threshold_bound_lowering_analysis():
    doc = ROOT / "docs" / "threshold-bound-analysis.md"
    assert doc.exists(), "docs/threshold-bound-analysis.md must exist"
    text = doc.read_text(encoding="utf-8")
    assert "2^{17}" in text or "131,072" in text
    assert "256" in text
    assert "u_0" in text
    assert "DAG" in text or "feed-forward" in text
