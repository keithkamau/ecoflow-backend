from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/pickups", tags=["pickups"])
@router.get("/")
def list_pickups(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_pickup(item_id:str,u=Depends(get_current_user)): return {"id":item_id,"status":"pending","scheduled_date":None}
@router.post("/")
def create_pickup(u=Depends(get_current_user)): return {"id":"placeholder"}
@router.put("/{item_id}/schedule")
def schedule_pickup(item_id:str,u=Depends(get_current_user)): return {"status":"scheduled"}
@router.put("/{item_id}/assign-driver")
def assign_driver(item_id:str,u=Depends(get_current_user)): return {"status":"driver_assigned"}
@router.put("/{item_id}/start")
def start_pickup(item_id:str,u=Depends(get_current_user)): return {"status":"in_transit"}
@router.put("/{item_id}/deliver")
def deliver_pickup(item_id:str,u=Depends(get_current_user)): return {"status":"delivered"}
@router.put("/{item_id}/confirm")
def confirm_pickup(item_id:str,u=Depends(get_current_user)): return {"status":"confirmed"}
@router.post("/{item_id}/proof")
def upload_proof(item_id:str,u=Depends(get_current_user)): return {"message":"proof uploaded"}
