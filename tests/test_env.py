from pathlib import Path

import pytest

from aegiseval.env import RUN_MARKER, TrialEnvironment


def test_trial_environment_copies_fixtures_and_tracks_artifacts(tmp_path: Path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "source.txt").write_text("source", encoding="utf-8")

    env = TrialEnvironment.create(task_id="task", fixtures_dir=fixtures, root=tmp_path / "trial")

    assert (tmp_path / "trial" / RUN_MARKER).exists()
    assert (env.workspace / "source.txt").read_text(encoding="utf-8") == "source"
    (env.workspace / "answer.md").write_text("answer", encoding="utf-8")

    artifacts = env.collect_artifacts(["answer.md"])
    assert artifacts[0].path == "answer.md"
    assert artifacts[0].exists is True
    assert artifacts[0].sha256


def test_trial_environment_reset_is_deterministic(tmp_path: Path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "source.txt").write_text("source", encoding="utf-8")

    first = TrialEnvironment.create("task", fixtures, tmp_path / "trial")
    (first.workspace / "junk.txt").write_text("junk", encoding="utf-8")
    second = TrialEnvironment.create("task", fixtures, tmp_path / "trial")

    assert not (second.workspace / "junk.txt").exists()
    assert (second.workspace / "source.txt").exists()


def test_trial_environment_refuses_to_delete_unmarked_non_empty_directory(tmp_path: Path):
    unsafe = tmp_path / "not-a-run"
    unsafe.mkdir()
    (unsafe / "important.txt").write_text("do not delete", encoding="utf-8")

    with pytest.raises(ValueError, match="unmarked non-empty"):
        TrialEnvironment.create("task", tmp_path / "missing-fixtures", unsafe)

    assert (unsafe / "important.txt").read_text(encoding="utf-8") == "do not delete"
