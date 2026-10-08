import json

from scripts.data.check import validate_dataset, validate_registry
from scripts.data.registry import DatasetManager, DatasetRegistry


def test_validate_fixture_dataset_reports_manifest_details():
    report = validate_dataset("furniture-fixture")

    assert report["name"] == "furniture-fixture"
    assert report["status"] == "ok"
    assert report["manifest"]["file_count"] == 1
    assert report["manifest"]["byte_size"] > 0
    assert len(report["manifest"]["sha256"]) == 64
    assert report["errors"] == []


def test_validate_fixture_rejects_duplicate_furniture_ids(tmp_path):
    fixture = tmp_path / "furniture.json"
    fixture.write_text(
        json.dumps(
            [
                {"id": "chair-001", "dimensions": [1, 1, 1]},
                {"id": "chair-001", "dimensions": [1, 1, 1]},
            ]
        ),
        encoding="utf-8",
    )
    registry_file = tmp_path / "registry.json"
    registry_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "datasets": [
                    {
                        "name": "bad-fixture",
                        "display_name": "Bad Fixture",
                        "purpose": "test",
                        "required": True,
                        "profile": "dev",
                        "acquisition": "local_fixture",
                        "status": "available",
                        "license_status": "project_fixture",
                        "source": "test",
                        "version": "v1",
                        "preprocessing_version": "v1",
                        "path": str(fixture),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    manager = DatasetManager(DatasetRegistry.from_path(registry_file), root=tmp_path)

    report = validate_dataset("bad-fixture", manager=manager)

    assert report["status"] == "invalid"
    assert "duplicate furniture id: chair-001" in report["errors"]


def test_validate_registry_reports_manual_datasets_without_hard_failure():
    reports = validate_registry()
    by_name = {report["name"]: report for report in reports}

    assert by_name["furniture-fixture"]["status"] == "ok"
    assert by_name["interior-style"]["status"] == "needs_user_confirmation"
    assert by_name["3d-front"]["status"] == "human_required"
