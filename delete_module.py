import os
import sys
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python delete_module.py [모듈명]")
        sys.exit(1)
    module = sys.argv[1]
    module_cap = module.capitalize()
    info_path = f"{module}/module_info.json"
    if not os.path.exists(info_path):
        print(f"module_info.json을 찾을 수 없습니다: {info_path}")
        sys.exit(1)
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    # backend, frontend, db 등 관련 파일/폴더 삭제
    safe_delete(info.get("backend", ""))
    safe_delete(info.get("frontend", ""))
    safe_delete(info.get("db", ""))
    # module_info.json 및 상위 폴더 삭제
    safe_delete(info_path)
    if os.path.exists(module) and not os.listdir(module):
        os.rmdir(module)
        print(f"[삭제] 폴더 {module}")

    # === [자동 등록 해제 안내 메시지] ===
    print(f"""
[가이드] FastAPI 백엔드 main.py에서 아래 코드를 삭제하세요!

from modules.{module}.routers import {module} as {module}_router
app.include_router({module}_router.router, prefix="/{module}")

--------------------------------------

[가이드] React App.js에서 아래 코드를 삭제하세요!

import {module_cap}Page from './modules/{module}';
// ...
<Route path="/{module}" element={{ <{module_cap}Page /> }} />
""")

    print(f"\n✅ '{module}' 모듈 관련 파일/폴더 삭제 완료!")
