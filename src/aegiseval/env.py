from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from aegiseval.schema import ArtifactRecord


@dataclass(frozen=True)
class TrialEnvironment:
    task_id: str
    workspace: Path

    @classmethod
    def create(cls, task_id: str, fixtures_dir: Path, root: Path) -> "TrialEnvironment":
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        workspace = root / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        if fixtures_dir.exists():
            for item in fixtures_dir.iterdir():
                target = workspace / item.name
                if item.is_dir():
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)
        return cls(task_id=task_id, workspace=workspace)

    def collect_artifacts(self, relative_paths: list[str]) -> list[ArtifactRecord]:
        return [self._record(path) for path in relative_paths]

    def _record(self, relative_path: str) -> ArtifactRecord:
        path = self.workspace / relative_path
        if not path.exists() or not path.is_file():
            return ArtifactRecord(path=relative_path, exists=False)
        data = path.read_bytes()
        return ArtifactRecord(
            path=relative_path,
            exists=True,
            sha256=hashlib.sha256(data).hexdigest(),
            size_bytes=len(data),
        )
