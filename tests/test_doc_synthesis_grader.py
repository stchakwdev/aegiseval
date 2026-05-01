from pathlib import Path

from aegiseval.graders.doc_synthesis import grade_doc_synthesis


def test_doc_synthesis_grader_accepts_required_claims_and_citations(tmp_path: Path):
    workspace = tmp_path
    (workspace / "sources").mkdir()
    (workspace / "sources" / "memo_a.md").write_text("Project Aurora reduced search time by 35%.", encoding="utf-8")
    (workspace / "sources" / "memo_b.md").write_text("The rollout risk is fabricated citations.", encoding="utf-8")
    (workspace / "final.md").write_text(
        "Project Aurora reduced search time by 35% [memo_a.md]. The key risk is fabricated citations [memo_b.md].",
        encoding="utf-8",
    )

    result = grade_doc_synthesis(workspace)

    assert result.passed is True
    assert result.score == 1.0


def test_doc_synthesis_grader_accepts_source_relative_citation_paths(tmp_path: Path):
    workspace = tmp_path
    (workspace / "sources").mkdir()
    (workspace / "sources" / "memo_a.md").write_text("Project Aurora reduced search time by 35%.", encoding="utf-8")
    (workspace / "sources" / "memo_b.md").write_text("The rollout risk is fabricated citations.", encoding="utf-8")
    (workspace / "final.md").write_text(
        "Project Aurora reduced search time by 35% [sources/memo_a.md]. The key risk is fabricated citations [sources/memo_b.md].",
        encoding="utf-8",
    )

    result = grade_doc_synthesis(workspace)

    assert result.passed is True
    assert result.score == 1.0


def test_doc_synthesis_grader_rejects_fabricated_citations(tmp_path: Path):
    workspace = tmp_path
    (workspace / "sources").mkdir()
    (workspace / "sources" / "memo_a.md").write_text("Project Aurora reduced search time by 35%.", encoding="utf-8")
    (workspace / "final.md").write_text("Project Aurora reduced search time by 35% [ghost.md].", encoding="utf-8")

    result = grade_doc_synthesis(workspace)

    assert result.passed is False
    assert any("ghost.md" in issue for issue in result.issues)
