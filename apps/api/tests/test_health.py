from fastapi.testclient import TestClient

from apps.api.app.main import app

c=TestClient(app)
def test_health(): assert c.get("/health").json()["status"]=="ok"
def test_ready(): assert c.get("/ready").json()["status"]=="ready"
