import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

FOLDERS = [
    "backend/app/modules",
    "backend/app/routers",
    "frontend/src/modules",
    "nginx",
    "db/modules",
    "db/data",
    "redis/data"
]

FILES = {
    ".gitignore": """
node_modules/
build/
dist/
frontend/build/
npm-debug.log
yarn-debug.log
yarn-error.log
pnpm-lock.yaml
frontend/.env
.env
.env.*
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
.DS_Store
Thumbs.db
.vscode/
.idea/
.history/
.AppleDouble
*.swp
db/data/
redis/data/
coverage.xml
.coverage
*.log
README.md
*.md
""",
    ".dockerignore": """
**/node_modules
**/build
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
    "README.md": "# PSA-NEXT 실무형 자동화 프로젝트 스켈레톤\n",
    "backend/app/main.py": '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ping")
def ping():
    return {"message": "pong"}
''',
    "backend/requirements.txt": """
fastapi
uvicorn
pymysql
bcrypt
""",
    "backend/Dockerfile.dev": """
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--reload"]
""",
    "backend/Dockerfile.prod": """
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0"]
""",
    "nginx/nginx.dev.conf": """
server {
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
}
""",
    "nginx/nginx.prod.conf": """
server {
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
}
""",
    "nginx/Dockerfile": """
FROM nginx:alpine
COPY nginx.dev.conf /etc/nginx/conf.d/default.conf
""",
    "docker-compose.dev.yml": """
version: "3.9"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./:/app
    environment:
      - PYTHONPATH=/app
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
    "docker-compose.prod.yml": """
version: "3.9"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - PYTHONPATH=/app
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
    ".env.dev": "EXAMPLE_KEY=dev\n",
    ".env.prod": "EXAMPLE_KEY=prod\n",
    "db/init.sql": "-- 필요시 개발용 초기 SQL 작성\n"
}

def make_folders():
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
        print(f'[폴더 생성] {folder}')

def make_files():
    for filepath, content in FILES.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.lstrip('\n'))
        print(f'[파일 생성] {filepath}')

if __name__ == '__main__':
    make_folders()
    make_files()
    print("\n✅ PSA-NEXT 실무형 도커/자동화 스켈레톤 생성 완료!")
    print("→ docker-compose -f docker-compose.dev.yml up 으로 바로 개발환경 실행하세요.")
    print("→ 도커파일/컨텍스트는 backend, nginx, frontend로만 분리되어 꼬일 일이 없습니다.")
