from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/payments", tags=["payments"])
@router.get("/")
def list_payments(u=Depends(get_current_user)): return []
@router.get("/{item_id}")
def get_payment(item_id:str,u=Depends(get_current_user)): return {}
@router.post("/")
def create_payment(u=Depends(get_current_user)): return {"id":"placeholder"}
@router.post("/mpesa/stk-push")
def mpesa_stk_push(u=Depends(get_current_user)): return {"message":"STK push sent","checkout_request_id":"ws_CO_test"}
@router.post("/mpesa/callback")
def mpesa_callback(): return {"ResultCode":0,"ResultDesc":"Success"}
