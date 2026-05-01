import pytest

from aegiseval.schema import TaskSpec


def test_task_spec_roundtrips_minimal_valid_task():
    spec = TaskSpec(
        id="doc_synthesis_001",
        version="0.1.0",
        domain="document_synthesis",
        instruction="Write a cited memo.",
        expected_artifacts=[{"path": "final.md", "kind": "markdown"}],
        grader={"name": "doc_synthesis", "kind": "code"},
    )

    payload = spec.model_dump()
    loaded = TaskSpec.model_validate(payload)

    assert loaded.id == "doc_synthesis_001"
    assert loaded.expected_artifacts[0].path == "final.md"


def test_task_spec_rejects_missing_expected_artifacts():
    with pytest.raises(ValueError):
        TaskSpec(
            id="bad",
            version="0.1.0",
            domain="document_synthesis",
            instruction="Do something",
            expected_artifacts=[],
            grader={"name": "doc_synthesis", "kind": "code"},
        )
