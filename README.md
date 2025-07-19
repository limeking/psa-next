# PSA-NEXT 실무형 도커 기반 모듈 자동화 시스템

---

## 📦 프로젝트 소개

**PSA-NEXT**는 FastAPI + React + MySQL + Redis + Nginx를  
완전히 도커 기반으로 통합,  
모듈/기능의 생성·삭제·동기화·배포까지 “실무에서 실수 없이” 자동화하는  
**진짜 실무형 인프라/운영 시스템**입니다.

- 개발/운영 환경 모두 완전히 동일한 자동화 구조
- 대시보드/CLI에서 트리뷰, 상태, 이벤트, 에러, 헬스체크, 배포까지 실시간 관리
- 전체 시스템 구조 및 모듈 현황을 **시각적으로 트리**로 확인
- 누구나 10분 만에 온보딩할 수 있는 실무형 자동화 템플릿

---

## 🛠️ 실무 자동화 전체 플로우

1. **프로젝트 전체 리셋/초기화**
    ```bash
    python automation/clean_project.py [--keep-frontend]
    ```

2. **프론트엔드 신규 생성 (필요시)**
    ```bash
    npx create-react-app frontend
    npm install react-router-dom
    python automation/add_frontend_dockerfiles.py frontend
    ```

3. **기본 스켈레톤 구조 자동 생성**
    ```bash
    python automation/setup_skeleton.py
    ```

4. **관리자 대시보드(sysadmin) 모듈 생성/삭제**
    ```bash
    python -m automation.setup_system_dashboard           # 생성
    python -m automation.setup_system_dashboard --delete  # 삭제
    ```

5. **(옵션) 기능 모듈 추가/삭제**
    ```bash
    python automation/add_module.py [모듈명]             # ex) python automation/add_module.py admin
    python automation/delete_module.py [모듈명]
    ```

6. **Nginx conf 전체 동기화**
    ```bash
    python automation/generate_nginx_conf.py
    ```

7. **라우터/임포트 자동 등록 확인**
    - `backend/app/main.py`와 `frontend/src/App.js`에서 import, route가 잘 반영됐는지 확인

8. **도커 개발 환경 실행**
    ```bash
    sh automation/run_dev.sh
    ```

9. **테스트/검증**
    - 브라우저/API로 각 기능 정상 동작 확인
        - http://localhost/sysadmin/status
        - http://localhost/sysadmin/module-tree

---

## 🗂️ 주요 폴더 구조

psa-next/
├── backend/ # FastAPI 백엔드
├── frontend/ # React 프론트엔드
├── db/ # MySQL 데이터/초기화
├── redis/ # Redis 데이터
├── nginx/ # Nginx 설정
├── automation/ # 모듈/구조 자동화 스크립트
├── setup_skeleton.py
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── ...

yaml
복사
편집

---

## ⚡ 주요 자동화 명령어/스크립트

- **구조/스켈레톤 자동화** : `python automation/setup_skeleton.py`
- **모듈 추가/삭제**         : `python automation/add_module.py [모듈명]`, `python automation/delete_module.py [모듈명]`
- **대시보드(sysadmin) 관리**: `python -m automation.setup_system_dashboard [--delete]`
- **Nginx conf 동기화**      : `python automation/generate_nginx_conf.py`
- **도커 개발환경 실행**     : `sh automation/run_dev.sh`

---

## 🖥️ 대시보드/CLI 관리 기능

- **모듈 트리구조 시각화**
- **상태/이벤트/에러/헬스 실시간 관리**
- **모듈/컨테이너 상태 변화 뱃지/알림/실시간 로그**
- **운영환경과 개발환경 완전 동일**

---

## 🛠️ 실무 주의점/FAQ

- **모듈명 중복/삭제 시** 라우트/구조 동기화 꼭 확인
- `.env`, `*.log`, `db/data/`, `redis/data/` 등 민감·임시 파일은 반드시 `.gitignore`로 관리
- **도커 볼륨/포트 충돌, Nginx location 누락 주의**
- **개발-운영 환경 구분**: `nginx.dev.conf`, `nginx.prod.conf`를 반드시 구분 사용
- **자동화 스크립트는 기존 파일/폴더를 덮어쓸 수 있으니 백업 필수**
- **개발/운영 환경 모두에서 실시간 테스트/검증 가능**

---

## 🤝 협업/브랜치 전략

- `main` : 운영/배포 기준, 안정적인 버전만 머지
- `feature/*` : 신규 기능/모듈별 브랜치
- `hotfix/*` : 운영 중 긴급 버그
- PR/MR 시 코드리뷰 & 자동 테스트 권장

---

## 📄 문서화/온보딩

- `README.md`, `docs/README.module.md`, `docs/README.deploy.md` 등 실무 가이드 제공
- 자동화 명령어/구조/운영법/확장법/트러블슈팅 항목은 최신화 유지
- 누구나 “10분 만에 전체 프로젝트 구조와 사용법 파악” 가능

---

## 🏁 실무형 요약

> **“PSA-NEXT는 도커 기반에서 기능/상태/배포/운영까지 한 번에 동기화·관리 가능한 실무형 통합 자동화 시스템입니다!”**

---

## 📢 문의/라이선스

- (조직/이름/라이선스/문의채널 등 필요에 따라 입력)

---

# PSA-NEXT:  
**실무에 진짜 필요한 자동화 인프라의 기준!**