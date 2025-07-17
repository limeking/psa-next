# automation/utils.py
import os
import subprocess
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_FILE = BASE_DIR / 'backend/app/main.py'
APP_JS_FILE = BASE_DIR / 'frontend/src/App.js'


def add_route_to_main(module_name):
    import_line = f"from backend.app.modules.{module_name}.routers import router as {module_name}_router"
    include_line = f"app.include_router({module_name}_router)"

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if import_line in ''.join(lines):
        return  # Already registered

    # Find app = FastAPI() line
    for i, line in enumerate(lines):
        if 'app = FastAPI()' in line:
            insert_index = i + 1
            break
    else:
        insert_index = len(lines)

    # Insert import before app = FastAPI()
    for i, line in enumerate(lines):
        if line.startswith('from') or line.startswith('import'):
            continue
        insert_import_index = i
        break
    else:
        insert_import_index = 0

    lines.insert(insert_import_index, import_line + '\n')
    lines.insert(insert_index + 1, include_line + '\n')

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def remove_route_from_main(module_name):
    import_line = f"from backend.app.modules.{module_name}.routers import router as {module_name}_router"
    include_line = f"app.include_router({module_name}_router)"

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [line for line in lines if import_line not in line and include_line not in line]

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def add_route_to_appjs(module_name):
    """
    - sysadmin은 SystemStatusPage, /sysadmin/status
    - 그 외는 {ModuleCap}Page, /{module}
    - 실제 파일/컴포넌트명과 정확히 맞춤
    """
    appjs_path = APP_JS_FILE

    if module_name == "sysadmin":
        import_line = "import SystemStatusPage from './modules/sysadmin/pages/SystemStatusPage';\n"
        route_line = '          <Route path="/sysadmin/status" element={<SystemStatusPage />} />\n'
    else:
        module_cap = module_name.capitalize()
        import_line = f"import {module_cap}Page from './modules/{module_name}';\n"
        route_line = f'          <Route path="/{module_name}" element={{ <{module_cap}Page /> }} />\n'

    # 파일 읽기
    with open(appjs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 이미 import 또는 라우트가 있으면 중복 삽입 방지
    if any(import_line.strip() in l.strip() for l in lines) and any(route_line.strip() in l.strip() for l in lines):
        return

    # import 라인 추가: 첫 import 라인 다음에 삽입
    insert_import_idx = 0
    for i, l in enumerate(lines):
        if l.strip().startswith("import"):
            insert_import_idx = i + 1
    lines.insert(insert_import_idx, import_line)

    # <Routes> 태그 위치 탐색
    routes_end = -1
    for i, l in enumerate(lines):
        if '</Routes>' in l:
            routes_end = i
            break

    if routes_end != -1:
        # </Routes> 바로 위에 route_line 삽입
        lines.insert(routes_end, route_line)
    else:
        print("[자동화경고] App.js에 <Routes> 태그가 없습니다. 직접 라우트 추가 필요!")

    # 파일로 다시 쓰기
    with open(appjs_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)




def remove_route_from_appjs(module_name):
    """
    - add_route_to_appjs와 완벽하게 1:1로 import/route 삭제
    """
    appjs_path = APP_JS_FILE

    if module_name == "sysadmin":
        import_line = "import SystemStatusPage from './modules/sysadmin/pages/SystemStatusPage';"
        route_line = '<Route path="/sysadmin/status" element={<SystemStatusPage />} />'
    else:
        module_cap = module_name.capitalize()
        import_line = f"import {module_cap}Page from './modules/{module_name}';"
        route_line = f'<Route path="/{module_name}" element={{ <{module_cap}Page /> }} />'

    with open(appjs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if import_line in line or route_line in line:
            continue
        new_lines.append(line)

    with open(appjs_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)



def run_generate_nginx():
    subprocess.run(['python', 'automation/generate_nginx_conf.py'], cwd=BASE_DIR)
