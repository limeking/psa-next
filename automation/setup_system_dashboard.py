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
    'routers.py': '''from fastapi import APIRouter, Request
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

FRONTEND_FILES = {
    'pages/SystemStatusPage.js': '''import React, { useEffect, useState } from 'react';
import { fetchSystemStatus, fetchModuleList, fetchEvents, createModule, deleteModule, restartBackend } from '../api/sysadmin';

function ModuleManager() {
  const [moduleName, setModuleName] = useState('');
  const [result, setResult] = useState(null);

  const handleCreate = async () => {
    setResult(null);
    const res = await createModule(moduleName);
    setResult(res);
  };

  const handleDelete = async () => {
    setResult(null);
    const res = await deleteModule(moduleName);
    setResult(res);
  };

  return (
    <div style={{margin: "2em 0", padding: "1em", border: "1px solid #ddd", borderRadius: "8px"}}>
      <h3>모듈 생성/삭제</h3>
      <input
        type="text"
        value={moduleName}
        onChange={e => setModuleName(e.target.value)}
        placeholder="모듈명"
        style={{marginRight: "1em"}}
      />
      <button onClick={handleCreate}>생성</button>
      <button onClick={handleDelete} style={{marginLeft: "1em"}}>삭제</button>
      {result && (
        <pre style={{marginTop: "1em", background: "#f8f8f8", padding: "1em", borderRadius: "6px"}}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

function ModuleList() {
  const [modules, setModules] = useState([]);
  useEffect(() => {
    fetchModuleList().then(setModules);
  }, []);
  if (!modules.length) return <div>모듈 없음</div>;
  return (
    <div>
      <h3>모듈 현황</h3>
      <table>
        <thead>
          <tr>
            <th>이름</th>
            <th>Backend</th>
            <th>Frontend</th>
            <th>DB</th>
            <th>Enabled</th>
            <th>Route</th>
          </tr>
        </thead>
        <tbody>
          {modules.map(m => (
            <tr key={m.name}>
              <td>{m.name}</td>
              <td>{m.backend ? "O" : "-"}</td>
              <td>{m.frontend ? "O" : "-"}</td>
              <td>{m.db ? "O" : "-"}</td>
              <td>{m.enabled ? "Y" : "N"}</td>
              <td>{m.route}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EventLog() {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    fetchEvents().then(res => setEvents(res.events || []));
  }, []);
  if (!events.length) return <div>이벤트 없음</div>;
  return (
    <div>
      <h3>최근 이벤트/에러 로그</h3>
      <ul>
        {events.map((e, idx) => (
          <li key={idx} style={{color: e.message.includes('ERROR') ? 'red' : e.message.includes('WARN') ? 'orange' : 'black'}}>
            {e.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

function SystemStatusPage() {
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [restartStatus, setRestartStatus] = useState(null)

  useEffect(() => {
    fetchSystemStatus()
      .then((data) => setStatus(data))
      .catch((err) => setStatus({ error: err.message }))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>로딩중...</div>;
  if (status.error) return <div>에러: {status.error}</div>;

  const handleRestart = async () => {
    setRestartStatus("서버 리스타트 진행중...");
    const res = await restartBackend();
    if (res.success) setRestartStatus("서버 리스타트 완료!");
    else setRestartStatus("에러: " + (res.stderr || res.error));
  };

  return (
    <div>
      <h2>시스템 상태 (환경: {status.env})</h2>
      <ModuleManager />
      <button onClick={handleRestart} style={{marginBottom: 16}}>서버 리스타트</button>
      {restartStatus && <div>{restartStatus}</div>}
      <table>
        <thead>
          <tr>
            <th>컨테이너</th><th>상태</th><th>이미지</th><th>ID</th>
          </tr>
        </thead>
        <tbody>
          {status.containers && status.containers.map((c, i) => (
            <tr key={c.name || i}>
              <td>{c.name}</td>
              <td>{c.status}</td>
              <td>{c.image ? c.image : '-'}</td>
              <td>{c.id ? c.id : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ModuleList />
      <EventLog />
    </div>
  );
}

export default SystemStatusPage;
''',

'pages/ModuleTreePage.js': '''import React, { useEffect, useState } from "react";

function renderTree(node) {
  if (!node) return null;
  if (node.children && node.children.length > 0) {
    return (
      <li>
        <strong>{node.name}</strong>
        <ul>
          {node.children.map((child, idx) => (
            <React.Fragment key={child.name + idx}>{renderTree(child)}</React.Fragment>
          ))}
        </ul>
      </li>
    );
  }
  return <li>{node.name}</li>;
}

export default function ModuleTreePage() {
  const [tree, setTree] = useState(null);

  useEffect(() => {
    fetch("/api/sysadmin/tree")
      .then(res => res.json())
      .then(setTree);
  }, []);

  if (!tree) return <div>트리 구조 불러오는 중...</div>;
  return (
    <div>
      <h2>PSA-NEXT 전체 구조 트리</h2>
      <ul>{renderTree(tree)}</ul>
    </div>
  );
}
''',

    'api/sysadmin.js': '''export async function fetchSystemStatus() {
  const res = await fetch('/api/sysadmin/status');
  return await res.json();
}
export async function fetchModuleList() {
  const res = await fetch('/api/sysadmin/modules');
  return await res.json();
}
export async function fetchEvents() {
  const res = await fetch('/api/sysadmin/events');
  return await res.json();
}
export async function createModule(moduleName) {
  const res = await fetch('/api/sysadmin/create_module', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: moduleName})
  });
  return await res.json();
}
export async function deleteModule(moduleName) {
  const res = await fetch('/api/sysadmin/delete_module', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: moduleName})
  });
  return await res.json();
}
export async function restartBackend() {
  const res = await fetch('/api/sysadmin/restart_backend', { method: 'POST' });
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
    add_route_to_appjs('sysadmin/module-tree')  # 트리뷰 경로 자동등록
    run_generate_nginx()             # Nginx location 자동 동기화
    print("✅ System dashboard module created & Nginx conf updated!")

def delete_sysadmin_module():
    shutil.rmtree(BACKEND_SYSADMIN, ignore_errors=True)
    shutil.rmtree(FRONTEND_SYSADMIN, ignore_errors=True)
    if DB_SYSADMIN.exists():
        DB_SYSADMIN.unlink()

    remove_route_from_main('sysadmin')
    remove_route_from_appjs('sysadmin')
    remove_route_from_appjs('sysadmin/module-tree')  # ⭐️ 이 한 줄 추가!
    run_generate_nginx()
    print("🗑️ System dashboard module deleted & Nginx conf updated!")

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
