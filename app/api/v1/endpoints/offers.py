from fastapi import APIRouter

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("/")
def list_offers():
    return {"message": "offers endpoint working"}
