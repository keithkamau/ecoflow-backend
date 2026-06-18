from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/")
def list_messages():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
def get_messages(item_id: str):
    return {"item": None}


@router.post("/")
def create_messages():
    return {"message": "messages created", "id": "placeholder"}
