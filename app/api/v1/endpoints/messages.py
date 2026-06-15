from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/")
def list_messages():
    return {"message": "messages endpoint working"}
