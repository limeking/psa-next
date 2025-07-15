import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

import datetime
import json

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[생성] {path}")

def add_route_to_appjs(module, module_cap):
    appjs_path = "frontend/src/App.js"
    import_line = f"import {module_cap}Page from './modules/{module}';"
    route_line = f"<Route path=\"/{module}\" element={{ <{module_cap}Page /> }} />"
    if not os.path.exists(appjs_path):
        print(f"[경고] App.js를 찾을 수 없습니다: {appjs_path}")
        return
    with open(appjs_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not any(import_line in line for line in lines):
        insert_idx = 0
        for idx, line in enumerate(lines):
            if line.strip().startswith("import") and "react" not in line.lower():
                insert_idx = idx + 1
        lines.insert(insert_idx, import_line + "\n")
    route_inserted = False
    new_lines = []
    for line in lines:
        if "<Routes>" in line and not route_inserted:
            new_lines.append(line)
            new_lines.append(f"          {route_line}\n")
            route_inserted = True
        else:
            new_lines.append(line)
    if not route_inserted:
        for i in range(len(new_lines) - 1, -1, -1):
            if "</Routes>" in new_lines[i]:
                new_lines.insert(i, f"          {route_line}\n")
                break
    with open(appjs_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("[수정] App.js import/Route 자동 추가 완료")

def add_router_to_mainpy(module, module_cap):
    mainpy_path = "backend/app/main.py"
    import_line = f"from backend.app.modules.{module}.routers import {module} as {module}_router"
    include_line = f"app.include_router({module}_router.router, prefix=\"/{module}\")"
    if not os.path.exists(mainpy_path):
        print(f"[경고] main.py를 찾을 수 없습니다: {mainpy_path}")
        return

    with open(mainpy_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # 1. import_line은 모든 import fastapi 다음에!
    import_insert_idx = 0
    for idx, line in enumerate(lines):
        if "app = FastAPI()" in line.replace(" ", ""):
            import_insert_idx = idx  # app = FastAPI() 선언 바로 위
            break
    lines.insert(import_insert_idx, import_line + "\n")

    # 2. include_line은 app = FastAPI() 선언 아래에만!
    include_insert_idx = 0
    for idx, line in enumerate(lines):
        if "app = FastAPI()" in line.replace(" ", ""):
            include_insert_idx = idx + 1
            break
    # 이미 있는지 체크
    if not any(include_line in line for line in lines):
        lines.insert(include_insert_idx, include_line + "\n")
    with open(mainpy_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("[수정] main.py import/include_router 자동 추가 완료")

def main():
    if len(sys.argv) < 2:
        print("사용법: python automation/add_module.py [모듈명]")
        sys.exit(1)
    module = sys.argv[1].lower()
    module_cap = module.capitalize()

    # 프론트
    write_file(
        f"frontend/src/modules/{module}/index.js",
        f'''import React from "react";
export default function {module_cap}Page() {{
  return <div>{module_cap} 모듈 페이지</div>;
}}
'''
    )
    backend_base = f"backend/app/modules/{module}"
    # 백엔드 라우터 (최소한의 라우터 코드)
    write_file(
        f"{backend_base}/routers/{module}.py",
        f'''from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def {module}_ping():
    return {{"msg": "{module_cap} API OK"}}
'''
    )
    # __init__.py 자동 생성 (폴더마다)
    write_file(f"{backend_base}/__init__.py", "")
    write_file(f"{backend_base}/routers/__init__.py", "")
    write_file(f"{backend_base}/models/{module}.py", f"# {module_cap} DB 모델 예시\n# from sqlalchemy import ...\n")
    write_file(f"{backend_base}/models/__init__.py", "")

    # DB
    write_file(
        f"db/modules/{module}/init.sql",
        f"""-- {module_cap} 관련 테이블 DDL
-- 아래 주석을 해제하고, 필요시 테이블을 직접 DROP/생성하세요!
-- DROP TABLE IF EXISTS {module};  -- (직접 DROP 시 사용)
-- CREATE TABLE {module} (...);
"""
    )
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    creator = os.getenv("USERNAME") or os.getenv("USER") or "unknown"
    info = {
        "name": module,
        "type": "기능모듈",
        "description": f"{module_cap} 기능 모듈 (자동 생성)",
        "created_at": created_at,
        "creator": creator,
        "enabled": True,
        "backend": backend_base,
        "frontend": f"frontend/src/modules/{module}",
        "db": f"db/modules/{module}"
    }
    write_file(
        f"{backend_base}/module_info.json",
        json.dumps(info, indent=2, ensure_ascii=False)
    )
    add_route_to_appjs(module, module_cap)
    add_router_to_mainpy(module, module_cap)
    print(f"\n✅ '{module}' 모듈 자동 생성 및 App.js/main.py 등록 완료!")

if __name__ == "__main__":
    main()
