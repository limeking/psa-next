import logging
from backend.app.core.logging_config import setup_logging
setup_logging()
logging.info("테스트 로그: PSA-NEXT 시스템 기동됨")
from fastapi import FastAPI

app = FastAPI()
from backend.app.modules.sysadmin.routers import router as sysadmin_router
app.include_router(sysadmin_router)

@app.get("/api/ping")
def ping():
    return {"message": "pong"}
