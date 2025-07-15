from fastapi import FastAPI
from backend.app.modules.admin.routers import admin as admin_router

app = FastAPI()

app.include_router(admin_router.router, prefix="/admin")

@app.get("/api/ping")
def ping():
    return {"message": "pong"}
