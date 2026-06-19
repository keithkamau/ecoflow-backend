from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
router = APIRouter(prefix="/listings", tags=["listings"])
@router.get("/")
def list_listings(): return []
@router.get("/mine")
def my_listings(u=Depends(get_current_user)): return []
@router.get("/materials")
def list_materials(): return [{"id":1,"name":"Plastic","unit":"kg"},{"id":2,"name":"Metal","unit":"kg"},{"id":3,"name":"Glass","unit":"kg"},{"id":4,"name":"Organic","unit":"kg"},{"id":5,"name":"E-Waste","unit":"kg"},{"id":6,"name":"Paper","unit":"kg"},{"id":7,"name":"Textile","unit":"kg"}]
@router.get("/recyclers/inventory")
def recycler_inventory(recycler_id:str=None,u=Depends(get_current_user)): return []
@router.get("/{listing_id}")
def get_listing(listing_id:str): return {"id":listing_id,"material":{"type":"plastic"},"quantity":0,"status":"waiting","location_address":"","price_expectation":0,"photos":[]}
@router.post("/")
def create_listing(u=Depends(get_current_user)): return {"id":"new-1","material":{"type":"plastic"},"quantity":0,"status":"waiting","location_address":"","price_expectation":0,"photos":[]}
@router.put("/{listing_id}")
def update_listing(listing_id:str,u=Depends(get_current_user)): return {"id":listing_id,"material":{"type":"plastic"},"quantity":0,"status":"waiting","location_address":"","price_expectation":0,"photos":[]}
@router.delete("/{listing_id}")
def delete_listing(listing_id:str,u=Depends(get_current_user)): return {"message":"deleted"}
