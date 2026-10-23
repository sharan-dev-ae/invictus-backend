import re
from app.schemas import TaskIn

def task_titles(prompt:str)->list[str]:
    lines=[re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*","",x).strip() for x in prompt.splitlines()]
    lines=[x for x in lines if x and not x.lower().startswith(("project:","milestone:"))]
    if len(lines)<2:lines=[x.strip().capitalize() for x in re.split(r"[.;]|\bthen\b|\band then\b",prompt,flags=re.I) if len(x.strip())>2]
    return list(dict.fromkeys(lines))[:20]
def generate_tasks(prompt,project_id=None,milestone_id=None):return [TaskIn(title=x[:250],project_id=project_id,milestone_id=milestone_id) for x in task_titles(prompt)]
