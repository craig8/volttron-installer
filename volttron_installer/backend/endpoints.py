from fastapi import APIRouter

ansible_router = APIRouter(prefix="/ansible")

@ansible_router.get("/inventory")
def get_inventory():
    return {"inventory": "inventory"}

