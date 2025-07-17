from fastapi import APIRouter

router = APIRouter(prefix="/sysadmin", tags=["System Admin"])

@router.get("/status")
def get_system_status():
    """
    서버 내부 건강상태만 간단 반환 (docker 명령 사용 안함)
    """
    return {"status": "ok", "containers": "docker 명령은 컨테이너에서 지원되지 않음"}
