from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_admin_status_reports_dataset_registry_state():
    client = TestClient(app)

    response = client.get("/admin/status")

    assert response.status_code == 200
    body = response.json()
    dataset_names = {dataset["name"] for dataset in body["datasets"]}
    assert "furniture-fixture" in dataset_names
    assert "interior-style" in dataset_names
    assert body["datasets_by_status"]["needs_user_confirmation"] >= 1
    assert body["datasets_by_status"]["human_required"] >= 1
