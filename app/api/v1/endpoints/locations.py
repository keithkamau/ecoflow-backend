from fastapi import APIRouter

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/")
def list_locations():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
def get_locations(item_id: str):
    return {"item": None}


@router.post("/")
def create_locations():
    return {"message": "locations created", "id": "placeholder"}
