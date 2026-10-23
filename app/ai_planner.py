import json
import httpx
from fastapi import HTTPException
from app.core.config import get_settings

TASK={"type":"object","additionalProperties":False,"properties":{"title":{"type":"string"},"estimated_minutes":{"type":"integer","minimum":1,"maximum":10080}},"required":["title","estimated_minutes"]}
SCHEMA={"type":"object","additionalProperties":False,"properties":{"project":{"anyOf":[{"type":"object","additionalProperties":False,"properties":{"title":{"type":"string"},"description":{"type":"string"}},"required":["title","description"]},{"type":"null"}]},"milestones":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"title":{"type":"string"},"tasks":{"type":"array","items":TASK}},"required":["title","tasks"]}},"standalone_tasks":{"type":"array","items":TASK}},"required":["project","milestones","standalone_tasks"]}

def plan_with_openai(prompt:str)->dict:
    settings=get_settings()
    if not settings.openai_api_key:raise HTTPException(503,"AI planning is not configured")
    payload={"model":settings.openai_model,"store":False,"instructions":"Convert the user's planning description into the smallest useful structure. Create a project only for a multi-step outcome. Create milestones only for meaningful stages. Put unrelated one-off work in standalone_tasks. Use concise action-oriented task titles.","input":prompt,"text":{"format":{"type":"json_schema","name":"invictus_plan","strict":True,"schema":SCHEMA}}}
    try:r=httpx.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {settings.openai_api_key}","Content-Type":"application/json"},json=payload,timeout=30)
    except httpx.HTTPError:raise HTTPException(503,"AI planning service unavailable")
    if r.status_code>=400:raise HTTPException(502,"AI planning request failed")
    data=r.json();text=next((c.get("text") for item in data.get("output",[]) if item.get("type")=="message" for c in item.get("content",[]) if c.get("type")=="output_text"),None)
    if not text:raise HTTPException(502,"AI planner returned no usable plan")
    return json.loads(text)
