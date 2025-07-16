# automation/setup_system_dashboard.py
import os
import shutil
import json
import datetime
from pathlib import Path
from automation.utils import (
    add_route_to_main, add_route_to_appjs, run_generate_nginx,
    remove_route_from_main, remove_route_from_appjs
)

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_SYSADMIN = BASE_DIR / 'backend/app/modules/sysadmin'
FRONTEND_SYSADMIN = BASE_DIR / 'frontend/src/modules/sysadmin'
DB_SYSADMIN = BASE_DIR / 'db/modules/sysadmin.sql'
MODULE_INFO_PATH = BACKEND_SYSADMIN / 'module_info.json'

BACKEND_FILES = {
    'routers.py': """from fastapi import APIRouter\n\nrouter = APIRouter(prefix=\"/sysadmin\", tags=[\"System Admin\"])\n\n@router.get(\"/status\")\ndef get_system_status():\n    return {\"status\": \"ok\"}""",
    'schemas.py': """from pydantic import BaseModel\n\nclass SystemStatus(BaseModel):\n    status: str""",
    'services.py': """def fetch_status():\n    return {\"status\": \"ok\"}""",
}

FRONTEND_FILES = {
    'pages/SystemStatusPage.jsx': """import React, { useEffect, useState } from 'react';\nimport { fetchSystemStatus } from '../api/sysadmin';\n\nfunction SystemStatusPage() {\n  const [status, setStatus] = useState(null);\n\n  useEffect(() => {\n    fetchSystemStatus().then((res) => setStatus(res.status));\n  }, []);\n\n  return (\n    <div>\n      <h1>System Dashboard</h1>\n      <p>Status: {status}</p>\n    </div>\n  );\n}\nexport default SystemStatusPage;""",
    'api/sysadmin.js': """export async function fetchSystemStatus() {\n  const res = await fetch('/sysadmin/status');\n  return await res.json();\n}""",
    'components/DummyBox.jsx': """import React from 'react';\nconst DummyBox = () => <div>Sysadmin Dummy Component</div>;\nexport default DummyBox;""",
}

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def write_module_info(module):
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    creator = os.getenv("USERNAME") or os.getenv("USER") or "unknown"
    info = {
        "name": module,
        "type": "관리자대시보드",
        "description": f"{module} 시스템 관리자 대시보드 (자동 생성)",
        "created_at": created_at,
        "creator": creator,
        "enabled": True,
        "backend": f"backend/app/modules/{module}",
        "frontend": f"frontend/src/modules/{module}",
        "db": f"db/modules/{module}.sql"
    }
    with open(MODULE_INFO_PATH, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

def create_sysadmin_module():
    ensure_dir(BACKEND_SYSADMIN)
    for filename, content in BACKEND_FILES.items():
        write_file(BACKEND_SYSADMIN / filename, content)

    for subdir_file, content in FRONTEND_FILES.items():
        target_path = FRONTEND_SYSADMIN / subdir_file
        ensure_dir(target_path.parent)
        write_file(target_path, content)

    write_file(DB_SYSADMIN, '-- sysadmin db structure')
    write_module_info('sysadmin')

    add_route_to_main('sysadmin')
    add_route_to_appjs('sysadmin')
    run_generate_nginx()

def delete_sysadmin_module():
    shutil.rmtree(BACKEND_SYSADMIN, ignore_errors=True)
    shutil.rmtree(FRONTEND_SYSADMIN, ignore_errors=True)
    if DB_SYSADMIN.exists():
        DB_SYSADMIN.unlink()

    remove_route_from_main('sysadmin')
    remove_route_from_appjs('sysadmin')
    run_generate_nginx()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='System Dashboard Setup/Delete')
    parser.add_argument('--delete', action='store_true', help='Delete system dashboard module')
    args = parser.parse_args()

    if args.delete:
        delete_sysadmin_module()
        print("🗑️ System dashboard module has been deleted.")
    else:
        create_sysadmin_module()
        print("✅ System dashboard module has been created.")
