from pathlib import Path

from aegiseval.redteam.artifact_spoofing import ArtifactSpoofingScanner
from aegiseval.redteam.citation_fabrication import CitationFabricationScanner


def run_redteam(workspace: Path) -> list[dict]:
    workspace.mkdir(parents=True, exist_ok=True)
    findings = [
        CitationFabricationScanner().scan(workspace / "citation"),
        ArtifactSpoofingScanner().scan(workspace / "artifact"),
    ]
    return [finding.model_dump() for finding in findings]
