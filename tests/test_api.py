import os
os.environ["DATA_PROVIDER"]="memory"
os.environ["AUTH_REQUIRED"]="false"
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health():assert c.get('/health').json()=={'status':'ok'}
def test_create_plan():
 r=c.post('/api/v1/plans',json={'title':'Test plan'});assert r.status_code==201;assert r.json()['title']=='Test plan'
def test_create_and_delete_task():
 r=c.post('/api/v1/tasks',json={'title':'Temporary task'});assert r.status_code==201
 task_id=r.json()['id'];assert c.delete(f'/api/v1/tasks/{task_id}').status_code==204
 assert all(x['id']!=task_id for x in c.get('/api/v1/workspace').json()['tasks'])
def test_prompt_creates_multiple_tasks():
 r=c.post('/api/v1/tasks/from-prompt',json={'prompt':'Research options. Compare costs. Make a decision.'})
 assert r.status_code==201;assert len(r.json())==3
def test_task_timer_lifecycle():
 task=c.post('/api/v1/tasks',json={'title':'Timed task','estimated_minutes':45}).json()
 assert task['estimated_minutes']==45 and task['status']=='Pending'
 started=c.patch(f"/api/v1/tasks/{task['id']}",json={'status':'In Progress'}).json();assert started['started_at']
 held=c.patch(f"/api/v1/tasks/{task['id']}",json={'status':'On Hold'}).json();assert held['started_at'] is None and held['status']=='On Hold'
