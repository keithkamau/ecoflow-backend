from fastapi import APIRouter

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
def list_listings():
    return {"message": "listings endpoint working"}
