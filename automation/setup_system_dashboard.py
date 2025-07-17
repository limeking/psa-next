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

# 1. 백엔드 sysadmin 라우터: docker 명령 없이 내부 상태만 반환!
BACKEND_FILES = {
    'routers.py': '''from fastapi import APIRouter

router = APIRouter(prefix="/sysadmin", tags=["System Admin"])

@router.get("/status")
def get_system_status():
    """
    서버 내부 건강상태만 간단 반환 (docker 명령 사용 안함)
    """
    return {"status": "ok", "containers": "docker 명령은 컨테이너에서 지원되지 않음"}
''',

    'schemas.py': '''from pydantic import BaseModel

class SystemStatus(BaseModel):
    status: str
    containers: dict = {}
''',

    'services.py': '''def fetch_status():
    """
    시스템 상태를 반환하는 서비스 함수 (확장용)
    """
    return {"status": "ok"}
''',
}

# 2. 프론트엔드(React) 컴포넌트: .js로 작성, 컨테이너 상태 출력
FRONTEND_FILES = {
        'pages/SystemStatusPage.js': '''import React, { useEffect, useState } from 'react';
import { fetchSystemStatus } from '../api/sysadmin';

function SystemStatusPage() {
  const [status, setStatus] = useState(null);
  const [containers, setContainers] = useState({});  // ← 반드시 {}로 초기화!

  useEffect(() => {
    fetchSystemStatus().then((res) => {
      setStatus(res.status);
      setContainers(res.containers);
    });
  }, []);

  return (
    <div>
      <h1>System Dashboard</h1>
      <p>Status: {status}</p>
      <h2>Containers</h2>
      <div>
        {/* 값이 문자열이면 그대로, 객체면 리스트로 안전하게 출력 */}
        {containers && typeof containers === "object" && Object.keys(containers).length > 0
          ? (
            <ul>
              {Object.entries(containers).map(([name, stat]) => (
                <li key={name}><strong>{name}</strong>: {stat}</li>
              ))}
            </ul>
          )
          : (
            <span>{containers ? containers.toString() : "정보 없음"}</span>
          )
        }
      </div>
    </div>
  );
}

export default SystemStatusPage;
''',

    'api/sysadmin.js': '''export async function fetchSystemStatus() {
  const res = await fetch('/api/sysadmin/status');
  return await res.json();
}
''',

    'components/DummyBox.js': '''import React from 'react';
const DummyBox = () => <div>Sysadmin Dummy Component</div>;
export default DummyBox;
''',
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

    add_route_to_main('sysadmin')    # FastAPI main.py에 라우터 자동 등록
    add_route_to_appjs('sysadmin')   # React App.js에 라우트 자동 등록
    run_generate_nginx()             # Nginx location 자동 동기화

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
