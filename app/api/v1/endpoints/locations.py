from fastapi import APIRouter
router = APIRouter(prefix="/locations", tags=["locations"])
@router.get("/")
def list_locations(): return []
@router.get("/nearby")
def nearby(): return []
