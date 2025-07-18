# automation/utils.py
import os
import subprocess
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_FILE = BASE_DIR / 'backend/app/main.py'
APP_JS_FILE = BASE_DIR / 'frontend/src/App.js'

def add_route_to_main(module_name):
    if module_name == "sysadmin":
        import_line = f"from backend.app.modules.sysadmin.routers import router as sysadmin_router"
        include_line = "app.include_router(sysadmin_router)"
    else:
        import_line = f"from backend.app.modules.{module_name}.routers.{module_name} import router as {module_name}_router"
        include_line = f"app.include_router({module_name}_router)"
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 이미 존재하면 중복 삽입 X
    if import_line in ''.join(lines):
        return

    # 마지막 import 라인 찾기
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import') or line.strip().startswith('from'):
            last_import_idx = i

    # app = FastAPI() 라인 찾기
    for i, line in enumerate(lines):
        if 'app = FastAPI()' in line:
            include_router_idx = i + 1
            break
    else:
        include_router_idx = len(lines)

    lines.insert(last_import_idx + 1, import_line + '\n')
    lines.insert(include_router_idx + 1, include_line + '\n')

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    sort_main_routes()

def remove_route_from_main(module_name):
    if module_name == "sysadmin":
        import_pattern = re.compile(r'from\s+backend\.app\.modules\.sysadmin\.routers\s+import router as sysadmin_router')
        include_pattern = re.compile(r'app\.include_router\(sysadmin_router\)')
    else:
        import_pattern = re.compile(rf'from\s+backend\.app\.modules\.{module_name}\.routers\.{module_name}\s+import router as {module_name}_router')
        include_pattern = re.compile(rf'app\.include_router\({module_name}_router.*\)')
    new_lines = []

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if import_pattern.search(line):
                continue
            if include_pattern.search(line):
                continue
            new_lines.append(line)

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    sort_main_routes()

def sort_main_routes():
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 분리
    import_lines = []
    include_lines = []
    other_lines = []
    for line in lines:
        # sysadmin
        if re.match(r'from backend\.app\.modules\.sysadmin\.routers import router as sysadmin_router', line):
            import_lines.append(line)
        # 일반 모듈
        elif re.match(r'from backend\.app\.modules\..+\.routers\..+ import router as .+_router', line):
            import_lines.append(line)
        elif re.match(r'app\.include_router\(sysadmin_router\)', line):
            include_lines.append(line)
        elif re.match(r'app\.include_router\(.+_router.*\)', line):
            include_lines.append(line)
        else:
            other_lines.append(line)

    # 정렬 + 중복제거
    import_lines_sorted = sorted(set(import_lines))
    include_lines_sorted = sorted(set(include_lines))

    # app = FastAPI() 위치 찾기
    output_lines = []
    inserted_imports = False
    inserted_includes = False
    for line in other_lines:
        output_lines.append(line)
        if not inserted_imports and 'app = FastAPI()' in line:
            output_lines.extend(import_lines_sorted)
            inserted_imports = True
        if not inserted_includes and 'app = FastAPI()' in line:
            output_lines.extend(include_lines_sorted)
            inserted_includes = True

    if not inserted_imports:
        output_lines.extend(import_lines_sorted)
    if not inserted_includes:
        output_lines.extend(include_lines_sorted)

    # 마지막으로 연속 빈 줄 1줄로 정리
    cleaned = []
    prev_blank = False
    for l in output_lines:
        if l.strip() == "":
            if not prev_blank:
                cleaned.append(l)
            prev_blank = True
        else:
            cleaned.append(l)
            prev_blank = False

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.writelines(cleaned)

def add_route_to_appjs(module_name):
    appjs_path = APP_JS_FILE

    if module_name == "sysadmin":
        import_line = "import SystemStatusPage from './modules/sysadmin/pages/SystemStatusPage';\n"
        route_line = '          <Route path="/sysadmin/status" element={<SystemStatusPage />} />\n'
    else:
        module_cap = module_name.capitalize()
        import_line = f"import {module_cap}Page from './modules/{module_name}';\n"
        route_line = f'          <Route path="/{module_name}" element={{ <{module_cap}Page /> }} />\n'

    with open(appjs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 이미 존재하면 중복 삽입 X
    if any(import_line.strip() in l.strip() for l in lines) and any(route_line.strip() in l.strip() for l in lines):
        return

    # import 정렬용
    import_lines = []
    route_lines = []
    other_lines = []

    for line in lines:
        if line.strip().startswith("import") and "from './modules/" in line:
            import_lines.append(line)
        elif line.strip().lstrip().startswith("<Route") and "element=" in line:
            route_lines.append(line)
        else:
            other_lines.append(line)

    # 새 라인 추가
    import_lines.append(import_line)
    route_lines.append(route_line)

    import_lines_sorted = sorted(set(import_lines))
    route_lines_sorted = sorted(set(route_lines))

    # <Routes> 태그 찾기
    output_lines = []
    inserted_imports = False
    inserted_routes = False
    for line in other_lines:
        if not inserted_imports and line.strip().startswith("import"):
            output_lines.extend(import_lines_sorted)
            inserted_imports = True
        if not inserted_routes and "<Routes>" in line:
            output_lines.append(line)
            output_lines.extend(route_lines_sorted)
            inserted_routes = True
            continue
        output_lines.append(line)

    if not inserted_routes:
        output_lines.extend(route_lines_sorted)

    with open(appjs_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

def remove_route_from_appjs(module_name):
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

    sort_appjs_routes()

def sort_appjs_routes():
    appjs_path = APP_JS_FILE
    with open(appjs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    import_lines = []
    route_lines = []
    other_lines = []
    for line in lines:
        if line.strip().startswith("import") and "from './modules/" in line:
            import_lines.append(line)
        elif line.strip().lstrip().startswith("<Route") and "element=" in line:
            route_lines.append(line)
        else:
            other_lines.append(line)

    import_lines_sorted = sorted(set(import_lines))
    route_lines_sorted = sorted(set(route_lines))

    output_lines = []
    inserted_imports = False
    inserted_routes = False
    for line in other_lines:
        if not inserted_imports and line.strip().startswith("import"):
            output_lines.extend(import_lines_sorted)
            inserted_imports = True
        if not inserted_routes and "<Routes>" in line:
            output_lines.append(line)
            output_lines.extend(route_lines_sorted)
            inserted_routes = True
            continue
        output_lines.append(line)
    if not inserted_routes:
        output_lines.extend(route_lines_sorted)

    # 마지막으로 연속 빈 줄 1줄로 정리
    cleaned = []
    prev_blank = False
    for l in output_lines:
        if l.strip() == "":
            if not prev_blank:
                cleaned.append(l)
            prev_blank = True
        else:
            cleaned.append(l)
            prev_blank = False

    with open(appjs_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned)

def run_generate_nginx():
    subprocess.run(['python', 'automation/generate_nginx_conf.py'], cwd=BASE_DIR)
