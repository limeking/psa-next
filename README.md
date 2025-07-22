# PSA-NEXT 실무형 도커 기반 모듈 자동화 시스템

---

## 📦 프로젝트 개요

**PSA-NEXT**는 FastAPI, React, MySQL, Redis, Nginx를 100% 도커 기반으로 통합하고  
모듈/기능의 생성·삭제·동기화·배포까지  
실무에서 실수 없이 완전 자동화하는 인프라/운영 시스템입니다.

- 개발/운영 환경 100% 일치  
- 대시보드·CLI에서 트리/상태/이벤트/에러/헬스/배포 실시간 관리  
- 10분 온보딩 가능한 실무형 자동화 템플릿

---

## 🛠️ 전체 자동화 플로우

### 프로젝트 전체 리셋/초기화

```bash
python automation/clean_project.py [--keep-frontend]
# PSA-NEXT 실무형 도커 기반 모듈 자동화 시스템

---

## 📦 프로젝트 개요

**PSA-NEXT**는 FastAPI, React, MySQL, Redis, Nginx를 100% 도커 기반으로 통합하고  
모듈/기능의 생성·삭제·동기화·배포까지  
실무에서 실수 없이 완전 자동화하는 인프라/운영 시스템입니다.

- 개발/운영 환경 100% 일치  
- 대시보드·CLI에서 트리/상태/이벤트/에러/헬스/배포 실시간 관리  
- 10분 온보딩 가능한 실무형 자동화 템플릿

---

## 🛠️ 전체 자동화 플로우

### 프로젝트 전체 리셋/초기화

프론트엔드 신규 생성 (필요시)
npx create-react-app frontend
npm install react-router-dom
python automation/add_frontend_dockerfiles.py


스켈레톤 구조 자동 생성
python -m automation.setup_system_dashboard           # 생성
python -m automation.setup_system_dashboard --delete  # 삭제


관리자 대시보드(sysadmin) 모듈 생성/삭제
python -m automation.setup_system_dashboard           # 생성
python -m automation.setup_system_dashboard --delete  # 삭제


기능 모듈 추가/삭제
python automation/add_module.py [모듈명]
python automation/delete_module.py [모듈명]


Nginx conf 전체 동기화
python automation/generate_nginx_conf.py


라우터/임포트 자동 등록 확인
backend/app/main.py, frontend/src/App.js에 import, route, include_router 자동 반영 확인

도커 개발 환경 실행
sh automation/run_dev.sh
# 또는
docker-compose -f docker-compose.dev.yml up --build


프론트엔드는 로컬에서 직접 npm start 권장

테스트/검증
http://localhost/sysadmin/status

http://localhost/sysadmin/module-tree


🗂️ 폴더 구조 예시
psa-next/
├── backend/         # FastAPI 백엔드
├── frontend/        # React 프론트엔드
├── db/              # MySQL 데이터/초기화
├── redis/           # Redis 데이터
├── nginx/           # Nginx 설정
├── automation/      # 모듈/구조 자동화 스크립트
├── setup_skeleton.py
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── ...


⚡️ 주요 자동화 스크립트/명령어
구조/스켈레톤 자동화:
python automation/setup_skeleton.py

모듈 추가/삭제:
python automation/add_module.py [모듈명]
python automation/delete_module.py [모듈명]

대시보드(sysadmin) 관리:
python -m automation.setup_system_dashboard [--delete]

Nginx conf 동기화:
python automation/generate_nginx_conf.py

도커 개발환경 실행:
sh automation/run_dev.sh

운영환경 빌드/실행:
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

🖥️ 대시보드/CLI 주요 기능
전체 시스템 트리 구조 시각화

상태/이벤트/에러/헬스 실시간 관리

모듈/컨테이너 상태 변화 뱃지/알림/실시간 로그

개발/운영 환경 완전 일치

🛠️ 실무 주의점/FAQ (2025-07 최신 기준)
모듈명 중복/삭제 시 라우트/구조 동기화 꼭 확인

.env, *.log, db/data/, redis/data/ 등 민감/임시 파일은 반드시 .gitignore로 관리

도커 볼륨/포트 충돌, Nginx location 누락 주의

개발-운영 환경 구분: nginx.dev.conf, nginx.prod.conf를 반드시 구분 사용

자동화 스크립트는 기존 파일/폴더를 덮어쓸 수 있으니 백업 필수

모듈/코드 변경 후 도커 빌드/재기동 루틴을 항상 프로젝트 루트에서 실행

컨테이너 내부 파일 반영 여부(라우터/코드/모듈) 직접 확인 습관!

운영/개발 환경 모두에서 실시간 테스트/검증 가능

🚨 운영 vs 개발 환경 차이 (중요!)
개발(dev)
백엔드/DB/Redis/nginx만 도커로 실행, 프론트는 로컬 npm start (핫리로드)

모듈 생성/삭제 후 build 없이 바로 반영

docker-compose.dev.yml에서 frontend 서비스 생략 가능

운영(prod)
소스는 항상 깃에서 pull & 최신 상태로 유지

반드시 npm run build 후 nginx 컨테이너에 mount

모듈 생성/삭제 후 운영 빌드/재기동 필수

운영 컨테이너에서만 파일/코드 생성 시, 재빌드시 사라짐!
→ 코드는 반드시 깃/로컬 소스에서만 관리

운영에서 파일/코드 생성 후엔 반드시 git/소스에도 반영

🤝 협업/브랜치 전략
main: 운영/배포 기준, 안정 버전만 머지

feature/*: 신규 기능/모듈별 브랜치

hotfix/*: 운영 중 긴급 버그 대응

PR/MR 시 코드리뷰 & 자동 테스트 권장

📄 문서화/온보딩
README.md, docs/README.module.md, docs/README.deploy.md 등 실무 가이드 제공

자동화 명령어/구조/운영법/트러블슈팅 항상 최신화

누구나 10분 만에 전체 구조와 사용법 파악 가능

📝 실무형 개발/운영 체크리스트
🔰 개발환경(dev)
docker-compose.dev.yml로 백엔드/DB/Redis/nginx만 도커로 실행

프론트엔드는 로컬에서만 npm start로 실행 (컨테이너 없이 핫리로드)

모듈 생성/삭제 자동화 후, 새 라우트/기능이 바로 반영되는지 확인

.env, db/data, redis/data 등 불필요한 파일은 반드시 .gitignore로 관리

자동화 스크립트로만 모듈/구조/라우트 관리 (수작업 금지)

🚦 운영환경(prod)
소스는 항상 깃에서 pull & 최신 상태로 유지

모듈 생성/삭제는 반드시 로컬/깃에서만 관리

운영 배포 전, 프론트엔드 npm run build 및 backend 빌드/업을 반드시 실행

빌드/업 이후 컨테이너 내부 라우트/코드/정적 파일 반영 여부 직접 확인

Nginx conf, 라우트, 트리, 상태, 대시보드, API, 이벤트 정상 동작 확인

운영 컨테이너에서 임의로 만든 파일/모듈은 다음 빌드 때 사라지는 것에 유의!

🏗️ 협업/온보딩
모든 신규 입장자, 협업자는 README, docs/README.module.md, docs/README.deploy.md 정독

온보딩 시 10분 내 전체 자동화/실행 경험 가능

브랜치 전략, PR/MR 리뷰, 코드/자동화 변경 내역 주기적 정리

⚠️ 실무 DevOps 경고/꿀팁
운영 컨테이너 내부에서 파일 생성/코드 변경 금지(반드시 소스/깃 기준)

자동화 구조/코드/스크립트는 자산! 절대 삭제 금지, 계속 개선/확장

운영 환경 반영= “빌드+업”까지 실행 후 반영 확인!

Nginx conf, 라우트 자동화 꼬임/누락 시 반드시 스크립트로 동기화/검증

🗃️ 로그/에러 관리 자동화 (2025-07 기준 신규 반영)
backend 로그: logs/backend/backend.log (도커/로컬 자동 동기화)

docker-compose에서 logs/backend:/var/log/psa-next 볼륨 마운트

로그 구조/로테이션/운영 정책:

backend/app/core/logging_config.py 참고

(운영 확장: Sentry, Slack, 중앙집중 로그 연동 가능)

nginx, db, 기타 컨테이너 로그도 logs/nginx, logs/mysql에 동일 방식 저장

🏁 실무형 요약
PSA-NEXT는 도커 기반에서
기능/상태/배포/운영까지 한 번에 동기화·관리 가능한
실무형 통합 자동화 시스템입니다.

실제 컨테이너 내부 파일/코드 반영 확인이 실전 DevOps의 핵심!

자동화 스크립트/구조는 절대 버리지 말고, 운영 습관/CI/CD로 계속 확장!

완전 자동화는 “실제 파일 반영 + 컨테이너 빌드/재기동”까지 검증이 필요!

📢 문의/라이선스
(조직/이름/라이선스/문의채널 등 필요시 입력)

PSA-NEXT: 실무에 진짜 필요한 자동화 인프라의 기준!
누구나 실전 DevOps 성장의 기반으로 활용할 수 있습니다!