"""Test suite verifying Theorem D.1 audit completeness (Task T11)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_theorem_d1_audit_document_exists():
    audit_file = ROOT / "docs" / "theorem-d1-audit.md"
    assert audit_file.exists(), "docs/theorem-d1-audit.md must exist"
    text = audit_file.read_text(encoding="utf-8")
    assert len(text) > 1000, "audit document must be substantive"
    assert "Theorem D.1" in text
    assert "2^{217}" in text or "2^217" in text
    assert "bipartite" in text.lower()
    assert "ring" in text.lower() or "z_{2^{" in text.lower() or "z_2" in text.lower()
