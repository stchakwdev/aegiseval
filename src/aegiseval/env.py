from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from aegiseval.schema import ArtifactRecord

RUN_MARKER = ".aegiseval-run"


@dataclass(frozen=True)
class TrialEnvironment:
    task_id: str
    workspace: Path

    @classmethod
    def create(cls, task_id: str, fixtures_dir: Path, root: Path) -> "TrialEnvironment":
        cls._prepare_run_root(root)
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

    @staticmethod
    def _prepare_run_root(root: Path) -> None:
        if root.is_symlink():
            raise ValueError(f"refusing to use symlink run directory: {root}")
        marker = root / RUN_MARKER
        if root.exists():
            if root.is_file():
                raise ValueError(f"run directory path is a file: {root}")
            if any(root.iterdir()) and not marker.exists():
                raise ValueError(
                    f"refusing to delete unmarked non-empty run directory: {root}. "
                    f"AegisEval only reuses directories containing {RUN_MARKER}."
                )
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        marker.write_text("managed by aegiseval\n", encoding="utf-8")

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
