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
    import_line = f"import {module_name.capitalize()}Page from './modules/{module_name}/pages/{module_name.capitalize()}Page';"
    route_line = f"<Route path=\"/{module_name}/status\" element={{<{module_name.capitalize()}Page />}} />"

    with open(APP_JS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    if import_line in content or route_line in content:
        return

    content = content.replace('import {', f'{import_line}\nimport {{')
    content = content.replace('</Routes>', f'  {route_line}\n    </Routes>')

    with open(APP_JS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


def remove_route_from_appjs(module_name):
    import_re = re.compile(rf"import .*{module_name.capitalize()}Page.*\n")
    route_re = re.compile(rf"\s*<Route path=\"/{module_name}/status\" element={{<.*?/>}} />\n")

    with open(APP_JS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if import_re.match(line) or route_re.match(line):
            continue
        new_lines.append(line)

    with open(APP_JS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def run_generate_nginx():
    subprocess.run(['python', 'automation/generate_nginx_conf.py'], cwd=BASE_DIR)
