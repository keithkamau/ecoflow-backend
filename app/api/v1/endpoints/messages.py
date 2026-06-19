from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/messages", tags=["messages"])
@router.get("/")
def list_messages(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_message(item_id:str,u=Depends(get_current_user)): return {}
@router.post("/")
def create_message(u=Depends(get_current_user)): return {"id":"placeholder"}
