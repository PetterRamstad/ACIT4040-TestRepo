from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_preference_round_and_feedback():
    c=TestClient(app)
    r=c.post('/preferences/rounds'); assert r.status_code==200 and len(r.json()['round'])==5
    item=r.json()['round'][0]['id']
    s=c.post('/preferences/feedback',json={'candidate_id':item,'value':'like'})
    assert s.status_code==200 and s.json()['liked']==[item]
