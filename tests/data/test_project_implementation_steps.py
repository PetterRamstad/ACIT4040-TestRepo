import json
from pathlib import Path


def test_project_implementation_steps_json_is_trackable():
    path = Path("docs/project_implementation_steps.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["project"] == "ACIT4040 AI Interior Design"
    assert data["source_plan"].endswith("ACIT4040_complete_project_and_dataset_plan.md")
    assert data["tracker_schema_version"] == 1

    step_ids = [step["id"] for step in data["steps"]]
    assert "dataset-registry-and-licensing" in step_ids
    assert "full-production-data-access" in step_ids

    for step in data["steps"]:
        assert step["status"] in {"done", "in_progress", "pending", "blocked"}
        assert isinstance(step["done"], bool)
        assert step["done"] is (step["status"] == "done")
        assert step["todo"]
        for item in step["todo"]:
            assert set(item) >= {"text", "done"}
            assert isinstance(item["done"], bool)
