from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_furniture_detail_and_unknown_id():
 c=TestClient(app); assert c.get('/furniture/chair-001').status_code==200; assert c.get('/furniture/nope').status_code==404
