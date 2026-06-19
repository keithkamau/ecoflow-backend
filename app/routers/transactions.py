from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/transactions", tags=["transactions"])
@router.get("/")
def list_transactions(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_transaction(item_id:str,u=Depends(get_current_user)): return {"id":item_id,"status":"pending","total_amount":0,"listing":{},"buyer":{},"seller":{}}
@router.post("/")
def create_transaction(u=Depends(get_current_user)): return {"id":"placeholder"}
@router.post("/{item_id}/review")
def review_transaction(item_id:str,u=Depends(get_current_user)): return {"message":"reviewed"}
