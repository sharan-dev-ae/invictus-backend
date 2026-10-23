from copy import deepcopy
from datetime import date,datetime,timedelta
from threading import RLock
from uuid import uuid4
from app.schemas import PlanIn,BucketIn

def _plan(title,status,priority,category,days,progress,description):
    return {"id":str(uuid4()),"title":title,"description":description,"status":status,"priority":priority,"category":category,"due_date":str(date.today()+timedelta(days=days)),"progress":progress,"updated_at":datetime.now().isoformat()}
_plans=[_plan("Launch portfolio refresh","In Progress","High","Career",2,72,"Polish case studies and publish the new site"),_plan("Train for the coastal 10K","In Progress","Medium","Health",8,45,"Build consistency with three weekly runs"),_plan("Plan Kyoto spring trip","Pending","Medium","Travel",18,20,"Map neighborhoods, stays and slow travel days"),_plan("Build a reading ritual","Completed","Low","Growth",-3,100,"Read twenty minutes before bed"),_plan("Create a home budget","On Hold","High","Finance",12,35,"Build a calm, sustainable monthly system"),_plan("Learn conversational Spanish","Pending","Low","Growth",30,10,"Practice useful phrases for upcoming travel")]
_buckets=[{"id":str(uuid4()),"title":"See the northern lights","category":"Travel","notes":"A quiet winter cabin, camera, and a clear sky."},{"id":str(uuid4()),"title":"Learn to make pottery","category":"Creative","notes":"Join a local studio and make a complete dinner set."},{"id":str(uuid4()),"title":"Run a half marathon","category":"Health","notes":"Train gradually and enjoy the process."}]

class MemoryRepository:
    def __init__(self):self.lock=RLock();self.plans={x["id"]:deepcopy(x) for x in _plans};self.buckets=deepcopy(_buckets);self.projects=[];self.milestones=[];self.tasks=[]
    def list_plans(self,owner_id=None):return list(self.plans.values())
    def create_plan(self,body:PlanIn,owner_id=None):
        with self.lock:
            x={"id":str(uuid4()),**body.model_dump(),"progress":0,"updated_at":datetime.now().isoformat()};self.plans[x["id"]]=x;return x
    def update_plan(self,pid,changes,owner_id=None):
        with self.lock:
            if pid not in self.plans:return None
            self.plans[pid].update(changes);self.plans[pid]["updated_at"]=datetime.now().isoformat();return self.plans[pid]
    def delete_plan(self,pid,owner_id=None):
        with self.lock:return self.plans.pop(pid,None) is not None
    def list_bucket_items(self,owner_id=None):return self.buckets
    def create_bucket_item(self,body:BucketIn,owner_id=None):
        with self.lock:
            x={"id":str(uuid4()),**body.model_dump()};self.buckets.append(x);return x
    def health(self):return True
    def workspace(self,owner_id):return {"projects":self.projects,"milestones":self.milestones,"tasks":self.tasks}
    def create_project(self,body,owner_id):
        x={"id":str(uuid4()),**body.model_dump(),"status":"Active"};self.projects.append(x);return x
    def create_milestone(self,body,owner_id):
        x={"id":str(uuid4()),**body.model_dump(),"completed":False};self.milestones.append(x);return x
    def create_task(self,body,owner_id):
        x={"id":str(uuid4()),**body.model_dump(),"completed":False,"position":len(self.tasks)};self.tasks.append(x);return x
    def update_task(self,task_id,changes,owner_id):
        x=next((x for x in self.tasks if x["id"]==task_id),None)
        if x:x.update(changes)
        return x
