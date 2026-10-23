import os
os.environ["DATA_PROVIDER"]="memory"
os.environ["AUTH_REQUIRED"]="false"
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health():assert c.get('/health').json()=={'status':'ok'}
def test_create_plan():
 r=c.post('/api/v1/plans',json={'title':'Test plan'});assert r.status_code==201;assert r.json()['title']=='Test plan'
