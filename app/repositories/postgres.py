from datetime import date,datetime,timezone
from uuid import UUID
from sqlalchemy import select,text
from sqlalchemy.orm import Session
from app.models import Activity,BucketListItem,Category,Plan,Project,Milestone,Task
from app.schemas import PlanIn,BucketIn

class PostgresRepository:
    def __init__(self,session:Session):self.session=session
    def _category(self,name:str):
        value=self.session.scalar(select(Category).where(Category.name==name))
        if not value:value=Category(name=name);self.session.add(value);self.session.flush()
        return value
    @staticmethod
    def _plan_dict(p:Plan):return {"id":str(p.id),"title":p.title,"description":p.description,"status":p.status,"priority":p.priority,"category":p.category.name if p.category else "Uncategorized","due_date":p.due_date.isoformat() if p.due_date else None,"progress":p.progress,"updated_at":p.updated_at.isoformat()}
    def list_plans(self,owner_id=None):
        query=select(Plan).order_by(Plan.updated_at.desc())
        if owner_id:query=query.where(Plan.owner_id==UUID(owner_id))
        return [self._plan_dict(p) for p in self.session.scalars(query).all()]
    def create_plan(self,body:PlanIn,owner_id=None):
        p=Plan(owner_id=UUID(owner_id) if owner_id else None,title=body.title,description=body.description,status=body.status,priority=body.priority,category=self._category(body.category),due_date=date.fromisoformat(body.due_date) if body.due_date else None,progress=0);self.session.add(p);self.session.flush();self.session.add(Activity(plan_id=p.id,action="created",details=p.title));self.session.commit();self.session.refresh(p);return self._plan_dict(p)
    def update_plan(self,pid,changes,owner_id=None):
        query=select(Plan).where(Plan.id==UUID(pid))
        if owner_id:query=query.where(Plan.owner_id==UUID(owner_id))
        p=self.session.scalar(query)
        if not p:return None
        if "category" in changes:p.category=self._category(changes.pop("category"))
        if "due_date" in changes:changes["due_date"]=date.fromisoformat(changes["due_date"]) if changes["due_date"] else None
        for key,value in changes.items():
            if hasattr(p,key):setattr(p,key,value)
        self.session.add(Activity(plan_id=p.id,action="updated",details=p.title));self.session.commit();self.session.refresh(p);return self._plan_dict(p)
    def delete_plan(self,pid,owner_id=None):
        query=select(Plan).where(Plan.id==UUID(pid))
        if owner_id:query=query.where(Plan.owner_id==UUID(owner_id))
        p=self.session.scalar(query)
        if not p:return False
        self.session.delete(p);self.session.commit();return True
    def list_bucket_items(self,owner_id=None):
        query=select(BucketListItem).order_by(BucketListItem.created_at.desc())
        if owner_id:query=query.where(BucketListItem.owner_id==UUID(owner_id))
        rows=self.session.scalars(query).all();return [{"id":str(x.id),"title":x.title,"category":x.category.name if x.category else "Uncategorized","notes":x.notes} for x in rows]
    def create_bucket_item(self,body:BucketIn,owner_id=None):
        x=BucketListItem(owner_id=UUID(owner_id) if owner_id else None,title=body.title,notes=body.notes,category=self._category(body.category));self.session.add(x);self.session.commit();self.session.refresh(x);return {"id":str(x.id),**body.model_dump()}
    def health(self):self.session.execute(text("SELECT 1"));return True
    @staticmethod
    def _project(x):return {"id":str(x.id),"title":x.title,"description":x.description,"status":x.status}
    @staticmethod
    def _milestone(x):return {"id":str(x.id),"project_id":str(x.project_id) if x.project_id else None,"title":x.title,"due_date":x.due_date.isoformat() if x.due_date else None,"completed":x.completed}
    @staticmethod
    def _task(x):return {"id":str(x.id),"project_id":str(x.project_id) if x.project_id else None,"milestone_id":str(x.milestone_id) if x.milestone_id else None,"title":x.title,"completed":x.completed,"status":x.status,"estimated_minutes":x.estimated_minutes,"accumulated_seconds":x.accumulated_seconds,"started_at":x.started_at.isoformat() if x.started_at else None,"position":x.position}
    def workspace(self,owner_id):
        owner=UUID(owner_id);return {"projects":[self._project(x) for x in self.session.scalars(select(Project).where(Project.owner_id==owner).order_by(Project.updated_at.desc())).all()],"milestones":[self._milestone(x) for x in self.session.scalars(select(Milestone).where(Milestone.owner_id==owner).order_by(Milestone.created_at)).all()],"tasks":[self._task(x) for x in self.session.scalars(select(Task).where(Task.owner_id==owner).order_by(Task.created_at.desc())).all()]}
    def create_project(self,body,owner_id):
        x=Project(owner_id=UUID(owner_id),title=body.title,description=body.description);self.session.add(x);self.session.commit();self.session.refresh(x);return self._project(x)
    def create_milestone(self,body,owner_id):
        x=Milestone(owner_id=UUID(owner_id),project_id=UUID(body.project_id) if body.project_id else None,title=body.title,due_date=date.fromisoformat(body.due_date) if body.due_date else None);self.session.add(x);self.session.commit();self.session.refresh(x);return self._milestone(x)
    def create_task(self,body,owner_id):
        x=Task(owner_id=UUID(owner_id),project_id=UUID(body.project_id) if body.project_id else None,milestone_id=UUID(body.milestone_id) if body.milestone_id else None,title=body.title,estimated_minutes=body.estimated_minutes);self.session.add(x);self.session.commit();self.session.refresh(x);return self._task(x)
    def update_task(self,task_id,changes,owner_id):
        x=self.session.scalar(select(Task).where(Task.id==UUID(task_id),Task.owner_id==UUID(owner_id)))
        if not x:return None
        next_status=changes.get("status")
        now=datetime.now(timezone.utc)
        if next_status and next_status!=x.status:
            if x.started_at and next_status in ("On Hold","Completed","Pending"):
                x.accumulated_seconds+=max(0,int((now-x.started_at).total_seconds()));x.started_at=None
            if next_status=="In Progress" and not x.started_at:x.started_at=now
            x.status=next_status;x.completed=next_status=="Completed"
        for key in ("title","completed","estimated_minutes"):
            if key in changes:setattr(x,key,changes[key])
        for key in ("project_id","milestone_id"):
            if key in changes:setattr(x,key,UUID(changes[key]) if changes[key] else None)
        self.session.commit();self.session.refresh(x);return self._task(x)
    def delete_task(self,task_id,owner_id):
        x=self.session.scalar(select(Task).where(Task.id==UUID(task_id),Task.owner_id==UUID(owner_id)))
        if not x:return False
        self.session.delete(x);self.session.commit();return True
