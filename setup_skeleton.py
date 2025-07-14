import os

folders = [
    'common', 'nginx', 'backend/app', 'db/data', 'redis/data', 'templates/backend_module/app', 'templates/frontend_module/src', 'templates/db_module'
]

files = {
        '.gitignore': """
# Node/React
node_modules/
build/
dist/
frontend/build/
npm-debug.log
yarn-debug.log
yarn-error.log
yarn.lock
pnpm-lock.yaml

# React 환경파일
frontend/.env
.env
.env.*
.env.local
.env.development
.env.production
*.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.mypy_cache/
.pytest_cache/
.venv/
venv/
.eggs/
*.egg-info/
.ipynb_checkpoints/
.sass-cache/

# OS/IDE/Editor
.DS_Store
Thumbs.db
.vscode/
.idea/
.history/
.AppleDouble
*.swp

# Docker Data
db/data/
redis/data/

# Test/Coverage/Logs
coverage.xml
.coverage
*.log

# Docs/MD
README.md
*.md
""",
    '.dockerignore': """
node_modules
build
dist
.git
.gitignore
.env
.env.*
db/data
redis/data
__pycache__/
*.pyc
*.pyo
*.log
.vscode
.idea
README.md
*.md
Dockerfile
""",
    'README.md': "# PSA-NEXT 실무형 자동화 프로젝트 스켈레톤\n",
    'backend/app/main.py': """
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ping")
async def ping():
    return {"message": "pong"}
""",
    'nginx/nginx.dev.conf': """server {
    listen 80;

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        proxy_pass http://host.docker.internal:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    # generate_nginx_conf.py에서 자동으로 덮어쓰기됨
}
""",
    'nginx/nginx.prod.conf': """server {
    listen 80;

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # generate_nginx_conf.py에서 자동으로 덮어쓰기됨
}
""",
    'nginx/Dockerfile': """
FROM nginx:alpine
COPY nginx.dev.conf /etc/nginx/conf.d/default.conf
""",
    'backend/Dockerfile.dev': """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
""",
    'backend/Dockerfile.prod': """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
""",
    'backend/requirements.txt': """
fastapi
uvicorn
pymysql
bcrypt
""",
    'docker-compose.dev.yml': """
version: "3.9"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend/app:/app/app
    env_file:
      - .env.dev
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: psa_db
    volumes:
      - ./db/data:/var/lib/mysql
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "13306:3306"

  redis:
    image: redis:7
    volumes:
      - ./redis/data:/data
    ports:
      - "6379:6379"

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    volumes:
      - ./nginx/nginx.dev.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - backend
""",
    'docker-compose.prod.yml': """
version: "3.9"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    env_file:
      - .env.prod
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: psa_db
    volumes:
      - ./db/data:/var/lib/mysql
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "13306:3306"

  redis:
    image: redis:7
    volumes:
      - ./redis/data:/data
    ports:
      - "6379:6379"

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - backend
""",
    '.env.dev': "EXAMPLE_KEY=dev\n",
    '.env.prod': "EXAMPLE_KEY=prod\n",
    'db/init.sql': "-- 필요시 개발용 초기 SQL 작성\n"
}


def make_generate_nginx_conf():
    nginx_conf_code = """
import os

# 개발모드(True)면 로컬 프론트(npm start), False면 운영(컨테이너) 프론트
dev_mode = True  # 필요시 직접 True/False 바꿔서 실행

modules = []
for name in os.listdir('.'):
    if os.path.isdir(name) and os.path.exists(f"{name}/backend/app"):
        modules.append(name)

if dev_mode:
    conf_path = "nginx/nginx.dev.conf"
    frontend_proxy = "proxy_pass http://host.docker.internal:3000;"
else:
    conf_path = "nginx/nginx.prod.conf"
    frontend_proxy = "proxy_pass http://frontend:80;"

with open(conf_path, "w", encoding="utf-8") as f:
    f.write("server {\\n    listen 80;\\n")
    for m in modules:
        f.write(f"    location /{m}/api/ " + "{\\n")
        f.write(f"        proxy_pass http://{m}-backend:8000/;\\n")
        f.write("    }\\n")
    f.write("    location / {\\n        " + frontend_proxy + "\\n    }\\n")
    f.write("}\\n")
print(f"✅ {conf_path} 자동생성 완료! (dev_mode={dev_mode})")
"""
    with open("nginx/generate_nginx_conf.py", "w", encoding="utf-8") as f:
        f.write(nginx_conf_code)
    print("[파일 생성] nginx/generate_nginx_conf.py")


def make_folders():
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f'[폴더 생성] {folder}')

def make_files():
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.lstrip('\n'))
        print(f'[파일 생성] {filepath}')


if __name__ == '__main__':
    make_folders()
    make_files()
    make_generate_nginx_conf()
    print("\n✅ 공통환경/템플릿/ignore 파일 자동생성 완료!")
    print("templates/ 폴더에 모듈 자동생성 템플릿도 미리 준비해 두세요.")
