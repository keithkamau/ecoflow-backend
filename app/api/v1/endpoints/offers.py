from fastapi import APIRouter

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/")
def list_offers():
    return {"items": [], "total": 0}


@router.get("/{item_id}")
def get_offers(item_id: str):
    return {"item": None}


@router.post("/")
def create_offers():
    return {"message": "offers created", "id": "placeholder"}
