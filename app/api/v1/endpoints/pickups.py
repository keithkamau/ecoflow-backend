from fastapi import APIRouter

router = APIRouter(prefix="/pickups", tags=["pickups"])


@router.get("/")
def list_pickups():
    return {"message": "pickups endpoint working"}
