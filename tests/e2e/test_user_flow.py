from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_vertical_flow():
 c=TestClient(app); assert c.get('/health').status_code==200; r=c.post('/preferences/rounds'); assert len(r.json()['round'])==5; assert c.post('/rooms',json={'width':4,'depth':4}).status_code==200
