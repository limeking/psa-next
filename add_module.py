import os
import sys

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[생성] {path}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python add_module.py [모듈명]")
        sys.exit(1)
    module = sys.argv[1]
    module_cap = module.capitalize()

    # 1. 프론트엔드 (React JS)
    write_file(
        f"frontend/src/modules/{module}/index.js",
        f"""import React from "react";
export default function {module_cap}Page() {{
  return <div>{module_cap} 모듈 페이지</div>;
}}
""")

    # 2. 백엔드 (FastAPI, backend/app/modules/ 경로로 강제)
    write_file(
        f"backend/app/modules/{module}/routers/{module}.py",
        f"""from fastapi import APIRouter

router = APIRouter()

@router.get("/{module}")
def get_{module}():
    return {{"msg": "{module_cap} API"}}
""")

    write_file(
        f"backend/app/modules/{module}/models/{module}.py",
        f"""# {module_cap} DB 모델 예시
# from sqlalchemy import ...
""")

    # 3. DB (SQL)
    write_file(
        f"db/modules/{module}/init.sql",
        f"""-- {module_cap} 관련 테이블 DDL
-- 아래 주석을 해제하고, 필요시 테이블을 직접 DROP/생성하세요!
-- DROP TABLE IF EXISTS {module};  -- (직접 DROP 시 사용)
-- CREATE TABLE {module} (...);
"""
    )

    # 4. 모듈 메타 정보 파일
    write_file(
        f"{module}/module_info.json",
        f"""{{
  "name": "{module}",
  "type": "기능모듈",
  "description": "{module_cap} 기능 모듈 (자동 생성)",
  "backend": "backend/app/modules/{module}",
  "frontend": "frontend/src/modules/{module}",
  "db": "db/modules/{module}"
}}
"""
    )

    # === [자동 등록/프록시 안내 메시지] ===
    print(f"""
[가이드] FastAPI 백엔드 main.py에 아래 코드를 추가하세요!

from modules.{module}.routers import {module} as {module}_router
app.include_router({module}_router.router, prefix="/{module}")

--------------------------------------

[가이드] React App.js에 아래 코드를 추가하세요!

import {module_cap}Page from './modules/{module}';
// ...
<Route path="/{module}" element={{ <{module_cap}Page /> }} />

--------------------------------------

[가이드] nginx.conf (nginx.dev.conf, nginx.prod.conf) location 블록에 아래 라인을 추가하거나,
generate_nginx_conf.py 스크립트를 실행하세요!

    location /{module}/ {{
        proxy_pass http://backend:8000/{module}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

""")

    print(f"\n✅ '{module}' 모듈(프론트/백엔드/DB) 자동 생성 완료!")

if __name__ == "__main__":
    main()
