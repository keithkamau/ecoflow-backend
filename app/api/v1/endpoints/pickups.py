from fastapi import APIRouter

router = APIRouter(prefix="/pickups", tags=["pickups"])


@router.get("/")
def list_pickups():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
def get_pickups(item_id: str):
    return {"item": None}


@router.post("/")
def create_pickups():
    return {"message": "pickups created", "id": "placeholder"}
