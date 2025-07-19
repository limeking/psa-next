from fastapi import APIRouter, Request
from automation.utils import run_generate_nginx
from pydantic import BaseModel
from pathlib import Path
import os
import json
import subprocess
import sys

router = APIRouter(prefix="/sysadmin", tags=["System Admin"])

@router.get("/status")
def get_system_status():
    """
    운영: docker sdk, 개발: mock 데이터 (구조 동일, 동작 동일!)
    """
    is_prod = os.getenv("PSA_PRODUCTION") == "1"
    if is_prod:
        try:
            import docker
            client = docker.from_env()
            containers = client.containers.list(all=True)
            status_list = [
                {
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags,
                    "id": c.short_id
                } for c in containers
            ]
            return {"containers": status_list, "env": "production"}
        except Exception as e:
            return {"error": str(e), "containers": [], "env": "production"}
    else:
        # 개발환경: mock 데이터 반환
        return {
            "containers": [
                {"name": "backend", "status": "running", "image": "psa-backend:dev", "id": "123abc"},
                {"name": "frontend", "status": "running", "image": "psa-frontend:dev", "id": "234bcd"},
                {"name": "db", "status": "running", "image": "mysql:8", "id": "345cde"},
                {"name": "nginx", "status": "running", "image": "nginx:latest", "id": "456def"},
                {"name": "redis", "status": "exited", "image": "redis:7", "id": "567efg"}
            ],
            "env": "dev"
        }

@router.get("/modules")
def get_modules_status():
    """
    PSA-NEXT 전체 모듈 현황 자동 조회
    """
    try:
        current_dir = Path(__file__).resolve()
        backend_dir = current_dir.parent.parent  # /app/backend/app/modules
        frontend_dir = current_dir.parent.parent.parent.parent / "frontend/src/modules"
        db_dir = current_dir.parent.parent.parent.parent / "db/modules"

        def module_meta(mod_name):
            meta_file = backend_dir / mod_name / 'module_info.json'
            if meta_file.exists():
                try:
                    with open(meta_file, encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    return {}
            return {}

        backend_modules = set()
        if backend_dir.exists():
            backend_modules = {p.name for p in backend_dir.iterdir() if p.is_dir()}

        frontend_modules = set()
        if frontend_dir.exists():
            frontend_modules = {p.name for p in frontend_dir.iterdir() if p.is_dir()}

        db_modules = set()
        if db_dir.exists():
            db_modules = {p.stem for p in db_dir.glob("*.sql")}

        all_modules = sorted(backend_modules | frontend_modules | db_modules)
        results = []
        for m in all_modules:
            results.append({
                "name": m,
                "backend": m in backend_modules,
                "frontend": m in frontend_modules,
                "db": m in db_modules,
                "enabled": module_meta(m).get("enabled", True),
                "route": f"/{m}",
                "meta": module_meta(m)
            })
        return results
    except Exception as e:
        return {"error": str(e)}

@router.get("/events")
def get_sysadmin_events():
    """
    최근 이벤트/에러 로그 반환 (운영: log 파일, 개발: mock data)
    """
    is_prod = os.getenv("PSA_PRODUCTION") == "1"
    try:
        if is_prod:
            log_file = Path("/var/log/psa-next-events.log")
            if log_file.exists():
                lines = log_file.read_text(encoding='utf-8', errors='ignore').splitlines()[-20:]
                return {"events": [ {"message": l} for l in lines ]}
            else:
                return {"events": [{"message": "(실운영 로그 파일이 없습니다)"}]}
        else:
            return {
                "events": [
                    {"message": "[INFO] 개발 환경 mock event #1"},
                    {"message": "[WARN] 개발 mock 경고 예시"},
                    {"message": "[ERROR] 임시 에러 로그: test failure"},
                    {"message": "[INFO] PSA-NEXT 개발환경 이벤트 #2"}
                ]
            }
    except Exception as e:
        return {"error": str(e), "events": []}

class ModuleName(BaseModel):
    name: str

@router.post("/create_module")
def create_module(data: ModuleName):
    """
    add_module.py를 통해 모듈 자동 생성
    """
    try:
        result = subprocess.run(
            [sys.executable, "automation/add_module.py", data.name],
            capture_output=True, text=True, cwd="/app"
        )
        run_generate_nginx()   # ⭐️ Nginx conf 자동 동기화
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/delete_module")
def delete_module(data: ModuleName):
    """
    delete_module.py를 통해 모듈 자동 삭제
    """
    try:
        result = subprocess.run(
            [sys.executable, "automation/delete_module.py", data.name],
            capture_output=True, text=True, cwd="/app"
        )
        run_generate_nginx()   # ⭐️ Nginx conf 자동 동기화
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/restart_backend")
def restart_backend():
    """
    backend 컨테이너만 docker compose로 리스타트
    """

    import shutil

    if not shutil.which("docker"):
        return {"success": False, "error": "docker CLI가 서버 환경에 설치/등록되어 있지 않습니다."}  

    try:
        result = subprocess.run(
            ["docker", "compose", "restart", "backend"],
            capture_output=True, text=True, cwd="/app"
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}     

@router.get("/tree")
def get_modules_tree():
    """
    PSA-NEXT 전체 구조/모듈 트리형 JSON 반환 (백엔드/프론트/DB 구조 통합)
    """
    try:
        current_dir = Path(__file__).resolve()
        backend_dir = current_dir.parent.parent
        frontend_dir = current_dir.parent.parent.parent.parent / "frontend/src/modules"
        db_dir = current_dir.parent.parent.parent.parent / "db/modules"

        def get_children(directory):
            if not directory.exists():
                return []
            items = []
            for p in sorted(directory.iterdir(), key=lambda x: x.name):
                if p.is_dir():
                    items.append({
                        "name": p.name,
                        "type": "folder",
                        "children": get_children(p)
                    })
                else:
                    items.append({
                        "name": p.name,
                        "type": "file"
                    })
            return items

        tree = {
            "name": "PSA-NEXT",
            "children": [
                {
                    "name": "backend",
                    "children": get_children(backend_dir)
                },
                {
                    "name": "frontend",
                    "children": get_children(frontend_dir)
                },
                {
                    "name": "db",
                    "children": get_children(db_dir)
                }
            ]
        }
        return tree
    except Exception as e:
        return {"error": str(e)}   

