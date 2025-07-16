from fastapi import APIRouter

router = APIRouter(prefix="/sysadmin", tags=["System Admin"])

@router.get("/status")
def get_system_status():
    return {"status": "ok"}