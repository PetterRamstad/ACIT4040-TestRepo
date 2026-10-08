from scripts.data.registry import DatasetManager, DatasetRegistry


def test_registry_exposes_required_and_manual_datasets():
    registry = DatasetRegistry.from_default()

    interior = registry.get("interior-style")
    deepfurniture = registry.get("deepfurniture")
    front = registry.get("3d-front")

    assert interior.required is True
    assert interior.status == "needs_user_confirmation"
    assert interior.acquisition == "confirm_source_url"
    assert "exact Kaggle URL" in interior.open_questions[0]

    assert deepfurniture.required is True
    assert deepfurniture.acquisition == "explicit_download"

    assert front.required is True
    assert front.acquisition == "manual_archive"


def test_dataset_manager_reports_manual_action_instead_of_downloading():
    result = DatasetManager().ensure("3d-future")

    assert result["name"] == "3d-future"
    assert result["status"] == "human_required"
    assert result["can_download_automatically"] is False
    assert "license" in result["message"].lower()


def test_fixture_dataset_is_reused_when_present():
    result = DatasetManager().ensure("furniture-fixture")

    assert result["name"] == "furniture-fixture"
    assert result["status"] == "reused"
    assert result["can_download_automatically"] is True
