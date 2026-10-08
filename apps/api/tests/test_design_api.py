from fastapi.testclient import TestClient
from apps.api.app.main import app

def test_layout_generation():
 c=TestClient(app); r=c.post('/layouts/generate',json={'room':{'width':6,'depth':6}}); assert r.status_code==200; assert r.json()['status']=='completed'
