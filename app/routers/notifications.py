from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/notifications", tags=["notifications"])
@router.get("/")
def list_notifications(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_notification(item_id:str,u=Depends(get_current_user)): return {}
@router.put("/{item_id}/read")
def mark_read(item_id:str,u=Depends(get_current_user)): return {"message":"marked read"}
