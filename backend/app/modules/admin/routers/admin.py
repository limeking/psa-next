from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def admin_ping():
    return {"msg": "Admin API OK"}
