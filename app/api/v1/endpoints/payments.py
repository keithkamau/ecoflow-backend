from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/")
def list_payments():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
def get_payments(item_id: str):
    return {"item": None}


@router.post("/")
def create_payments():
    return {"message": "payments created", "id": "placeholder"}
