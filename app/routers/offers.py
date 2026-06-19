from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/offers", tags=["offers"])
@router.get("/")
def list_offers(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_offer(item_id:str,u=Depends(get_current_user)): return {}
@router.post("/")
def create_offer(u=Depends(get_current_user)): return {"id":"placeholder"}
@router.put("/{item_id}/accept")
def accept_offer(item_id:str,u=Depends(get_current_user)): return {"status":"accepted"}
@router.put("/{item_id}/reject")
def reject_offer(item_id:str,u=Depends(get_current_user)): return {"status":"rejected"}
