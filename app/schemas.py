from pydantic import BaseModel, Field

class PlanIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);description:str="";status:str="Pending";priority:str="Medium";category:str="Personal";due_date:str|None=None
class BucketIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);category:str="Life";notes:str=""
class SignUpIn(BaseModel):
    email:str;password:str=Field(min_length=8);display_name:str=Field(min_length=1,max_length=80)
class SignInIn(BaseModel):
    email:str;password:str
class ProjectIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);description:str=""
class MilestoneIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);project_id:str|None=None;due_date:str|None=None
class TaskIn(BaseModel):
    title:str=Field(min_length=1,max_length=250);project_id:str|None=None;milestone_id:str|None=None
class PromptIn(BaseModel):
    prompt:str=Field(min_length=3,max_length=5000);project_id:str|None=None;milestone_id:str|None=None
