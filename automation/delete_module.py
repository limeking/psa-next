import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

import json
import shutil

def safe_delete(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"[삭제] 폴더 {path}")
        else:
            os.remove(path)
            print(f"[삭제] 파일 {path}")

def remove_route_from_appjs(module, module_cap):
    appjs_path = "frontend/src/App.js"
    import_line = f"import {module_cap}Page from './modules/{module}';"
    route_line = f"<Route path=\"/{module}\" element={{ <{module_cap}Page /> }} />"
    if not os.path.exists(appjs_path):
        print(f"[경고] App.js를 찾을 수 없습니다: {appjs_path}")
        return
    with open(appjs_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if import_line in line or route_line in line:
            continue
        new_lines.append(line)
    with open(appjs_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("[수정] App.js import/Route 자동 삭제 완료")

def remove_router_from_mainpy(module, module_cap):
    mainpy_path = "backend/app/main.py"
    import_line = f"from modules.{module}.routers import {module} as {module}_router"
    include_line = f"app.include_router({module}_router.router, prefix=\"/{module}\")"
    if not os.path.exists(mainpy_path):
        print(f"[경고] main.py를 찾을 수 없습니다: {mainpy_path}")
        return
    with open(mainpy_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if import_line in line or include_line in line:
            continue
        new_lines.append(line)
    with open(mainpy_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("[수정] main.py import/include_router 자동 삭제 완료")

def main():
    if len(sys.argv) < 2:
        print("사용법: python automation/delete_module.py [모듈명]")
        sys.exit(1)
    module = sys.argv[1].lower()
    module_cap = module.capitalize()
    info_path = f"backend/app/modules/{module}/module_info.json"
    if not os.path.exists(info_path):
        print(f"[경고] {info_path} (backend/app/modules/{module}/module_info.json)를 찾을 수 없습니다.")
        print("폴더만 직접 삭제합니다.")
        backend_path = f"backend/app/modules/{module}"
        frontend_path = f"frontend/src/modules/{module}"
        db_path = f"db/modules/{module}"
    else:
        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)
        backend_path = info.get("backend", f"backend/app/modules/{module}")
        frontend_path = info.get("frontend", f"frontend/src/modules/{module}")
        db_path = info.get("db", f"db/modules/{module}")

    # __init__.py를 백엔드 폴더에서 찾아서 개별 삭제
    for path in [
        f"{backend_path}/__init__.py",
        f"{backend_path}/routers/__init__.py",
        f"{backend_path}/models/__init__.py"
    ]:
        if os.path.exists(path):
            os.remove(path)
            print(f"[삭제] {path}")

    safe_delete(backend_path)
    safe_delete(frontend_path)
    safe_delete(db_path)
    safe_delete(info_path)
    module_folder = os.path.dirname(info_path) if os.path.exists(info_path) else f"backend/app/modules/{module}"
    if os.path.exists(module_folder) and not os.listdir(module_folder):
        os.rmdir(module_folder)
        print(f"[삭제] 폴더 {module_folder}")
    remove_route_from_appjs(module, module_cap)
    remove_router_from_mainpy(module, module_cap)
    print(f"\n✅ '{module}' 모듈 관련 파일/폴더 및 App.js/main.py, __init__.py 코드 자동 삭제 완료!")

if __name__ == "__main__":
    main()
