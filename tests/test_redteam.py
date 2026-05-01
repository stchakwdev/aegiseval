from pathlib import Path

from aegiseval.redteam.artifact_spoofing import ArtifactSpoofingScanner
from aegiseval.redteam.citation_fabrication import CitationFabricationScanner


def test_citation_fabrication_scanner_reports_unresolved_citation(tmp_path: Path):
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "memo_a.md").write_text("Project Aurora reduced search time by 35%.", encoding="utf-8")

    finding = CitationFabricationScanner().scan(tmp_path)

    assert finding.exploit_found is True
    assert "citation" in finding.title.lower()


def test_artifact_spoofing_scanner_reports_invalid_json(tmp_path: Path):
    finding = ArtifactSpoofingScanner().scan(tmp_path)

    assert finding.exploit_found is True
    assert finding.severity in {"medium", "high"}
