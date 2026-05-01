from pathlib import Path

from aegiseval.env import TrialEnvironment


def test_trial_environment_copies_fixtures_and_tracks_artifacts(tmp_path: Path):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "source.txt").write_text("source", encoding="utf-8")

    env = TrialEnvironment.create(task_id="task", fixtures_dir=fixtures, root=tmp_path / "trial")

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
