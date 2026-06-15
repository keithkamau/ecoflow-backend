from fastapi import APIRouter

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/")
def list_locations():
    return {"message": "locations endpoint working"}
