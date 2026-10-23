from fastapi import Depends,FastAPI,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import get_settings
from app.dependencies import get_repository
from app.repositories.base import Repository
from app.schemas import BucketIn,PlanIn
from app.schemas import SignInIn,SignUpIn,ProjectIn,MilestoneIn,TaskIn,PromptIn
from app.planner import generate_tasks
from app.ai_planner import plan_with_openai
from app.auth import CurrentUser,auth_request,current_user

settings=get_settings();app=FastAPI(title="Invictus Personal Command Center",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_methods=["*"],allow_headers=["*"])
@app.exception_handler(SQLAlchemyError)
async def database_error(_:Request,exc:SQLAlchemyError):return JSONResponse(status_code=503,content={"detail":"Database operation failed"})
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/api/v1/health/database")
def database_health(repo:Repository=Depends(get_repository)):
    try:return {"status":"ok" if repo.health() else "unavailable","provider":settings.data_provider}
    except SQLAlchemyError:raise HTTPException(503,"Database unavailable")
@app.post("/api/v1/auth/signup")
def signup(body:SignUpIn):return auth_request("POST","/auth/v1/signup",{"email":body.email,"password":body.password,"data":{"display_name":body.display_name}})
@app.post("/api/v1/auth/signin")
def signin(body:SignInIn):return auth_request("POST","/auth/v1/token?grant_type=password",body.model_dump())
@app.post("/api/v1/auth/refresh")
def refresh(body:dict):return auth_request("POST","/auth/v1/token?grant_type=refresh_token",{"refresh_token":body.get("refresh_token")})
@app.get("/api/v1/auth/me")
def me(user:CurrentUser=Depends(current_user)):return {"id":user.id,"email":user.email,"display_name":user.display_name}
@app.post("/api/v1/auth/signout",status_code=204)
def signout(authorization:str|None=None):return None
@app.get("/api/v1/workspace")
def workspace(repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.workspace(user.id)
@app.post("/api/v1/projects",status_code=201)
def create_project(body:ProjectIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.create_project(body,user.id)
@app.post("/api/v1/milestones",status_code=201)
def create_milestone(body:MilestoneIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.create_milestone(body,user.id)
@app.post("/api/v1/tasks",status_code=201)
def create_task(body:TaskIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.create_task(body,user.id)
@app.patch("/api/v1/tasks/{task_id}")
def update_task(task_id:str,body:dict,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    value=repo.update_task(task_id,body,user.id)
    if not value:raise HTTPException(404,"Task not found")
    return value
@app.delete("/api/v1/tasks/{task_id}",status_code=204)
def delete_task(task_id:str,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    if not repo.delete_task(task_id,user.id):raise HTTPException(404,"Task not found")
@app.post("/api/v1/tasks/from-prompt",status_code=201)
def tasks_from_prompt(body:PromptIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    if settings.planner_provider=="openai":
        plan=plan_with_openai(body.prompt);project_id=body.project_id
        if plan["project"] and not project_id:project_id=repo.create_project(ProjectIn(**plan["project"]),user.id)["id"]
        created=[]
        for milestone in plan["milestones"]:
            mid=repo.create_milestone(MilestoneIn(title=milestone["title"],project_id=project_id),user.id)["id"]
            created.extend(repo.create_task(TaskIn(**task,project_id=project_id,milestone_id=mid),user.id) for task in milestone["tasks"])
        created.extend(repo.create_task(TaskIn(**task,project_id=project_id,milestone_id=body.milestone_id),user.id) for task in plan["standalone_tasks"])
        return created
    drafts=generate_tasks(body.prompt,body.project_id,body.milestone_id)
    if not drafts:raise HTTPException(422,"Describe at least one actionable task")
    return [repo.create_task(x,user.id) for x in drafts]
@app.get("/api/v1/plans")
def get_plans(repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.list_plans(user.id)
@app.post("/api/v1/plans",status_code=201)
def create_plan(body:PlanIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.create_plan(body,user.id)
@app.patch("/api/v1/plans/{pid}")
def update_plan(pid:str,body:dict,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    try:value=repo.update_plan(pid,body,user.id)
    except ValueError:raise HTTPException(422,"Invalid plan identifier or date")
    if not value:raise HTTPException(404,"Plan not found")
    return value
@app.delete("/api/v1/plans/{pid}",status_code=204)
def delete_plan(pid:str,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    try:deleted=repo.delete_plan(pid,user.id)
    except ValueError:raise HTTPException(422,"Invalid plan identifier")
    if not deleted:raise HTTPException(404,"Plan not found")
@app.get("/api/v1/bucket-list")
def get_bucket(repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.list_bucket_items(user.id)
@app.post("/api/v1/bucket-list",status_code=201)
def create_bucket(body:BucketIn,repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):return repo.create_bucket_item(body,user.id)
@app.get("/api/v1/dashboard")
def dashboard(repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    vals=repo.list_plans(user.id);completed=sum(x["status"]=="Completed" for x in vals);active=sum(x["status"]=="In Progress" for x in vals);pending=sum(x["status"]=="Pending" for x in vals)
    return {"stats":{"total":len(vals),"active":active,"completed":completed,"pending":pending,"completion":round(sum(x["progress"] for x in vals)/len(vals)) if vals else 0},"today":[x for x in vals if x["status"]=="In Progress"][:3],"upcoming":sorted([x for x in vals if x["due_date"]],key=lambda x:x["due_date"])[:4],"recent":sorted(vals,key=lambda x:x["updated_at"],reverse=True)[:4]}
@app.get("/api/v1/insights")
def insights(repo:Repository=Depends(get_repository),user:CurrentUser=Depends(current_user)):
    vals=repo.list_plans(user.id);return {"by_status":{s:sum(p["status"]==s for p in vals) for s in ["Pending","On Hold","In Progress","Completed"]}}
@app.post("/api/v1/reset")
def reset():
    if settings.data_provider!="memory":raise HTTPException(403,"Reset is only available in memory mode")
    return {"message":"Demo data is already active"}
