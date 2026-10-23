from dataclasses import dataclass
import httpx
from fastapi import Header,HTTPException
from app.core.config import get_settings

@dataclass
class CurrentUser:
    id:str;email:str;display_name:str

def _headers(token:str|None=None):
    key=get_settings().supabase_anon_key
    if not key:raise HTTPException(503,"Authentication is not configured")
    value={"apikey":key,"Content-Type":"application/json"}
    if token:value["Authorization"]=f"Bearer {token}"
    return value

def auth_request(method:str,path:str,payload:dict|None=None,token:str|None=None):
    try:r=httpx.request(method,get_settings().supabase_url+path,headers=_headers(token),json=payload,timeout=12)
    except httpx.HTTPError:raise HTTPException(503,"Authentication service unavailable")
    data=r.json() if r.content else {}
    if r.status_code>=400:raise HTTPException(r.status_code,data.get("msg") or data.get("error_description") or "Authentication failed")
    return data

def current_user(authorization:str|None=Header(default=None))->CurrentUser:
    settings=get_settings()
    if not settings.auth_required:return CurrentUser("00000000-0000-0000-0000-000000000000","demo@orbit.local","Demo User")
    if not authorization or not authorization.startswith("Bearer "):raise HTTPException(401,"Sign in required")
    data=auth_request("GET","/auth/v1/user",token=authorization[7:])
    return CurrentUser(data["id"],data.get("email","") ,data.get("user_metadata",{}).get("display_name") or data.get("email","").split("@")[0])
