# 🔍 LookUp - 의류 가격 추적 플랫폼

**플랫폼 독립적인 의류 가격 추적 및 역대 최저가 알림 서비스**

LookUp은 무신사, 29cm, 지그재그 등 여러 패션 플랫폼의 상품 가격을 자동으로 추적하고, 사용자에게 역대 최저가 알림을 제공하는 서비스입니다.

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [시작하기](#-시작하기)
- [환경 변수 설정](#-환경-변수-설정)
- [아키텍처](#-아키텍처)
- [데이터베이스 설계](#-데이터베이스-설계)
- [크롤링 파이프라인](#-크롤링-파이프라인)
- [개발 가이드](#-개발-가이드)
- [보안 및 주의사항](#-보안-및-주의사항)

---

## 🎯 프로젝트 개요

### 핵심 기능
- ✅ **멀티 플랫폼 지원**: 무신사(1차) → 29cm(2차) → 지그재그 등 지속 확장
- 📊 **가격 추적**: 실시간 가격 변동 모니터링
- 🔔 **최저가 알림**: 역대 최저가 도달 시 사용자 알림
- 🔄 **자동 크롤링**: 3단계 계층 구조의 효율적인 데이터 수집

### 플랫폼 확장 로드맵
1. **1차**: 무신사 (Musinsa)
2. **2차**: 29cm
3. **3차**: 지그재그 (Zigzag)
4. **향후**: 기타 패션 플랫폼

---

## 🛠 기술 스택

### Backend & Crawler
- **언어**: Python 3.12+
- **패키지 관리**: uv (필수)
- **웹 크롤링**: Playwright (브라우저 제어) + BeautifulSoup4 (HTML 파싱)
- **데이터베이스**: PostgreSQL 16
- **마이그레이션**: Alembic

### Frontend
- **프레임워크**: Flutter / Next.js (TBD)

### Infrastructure
- **컨테이너화**: Docker & Docker Compose
- **아키텍처**: Monorepo
- **호스팅**: Oracle Cloud Infrastructure (Self-hosted PostgreSQL)
- **네트워크**: SSH 터널링 (Port 5432)

---

## 📁 프로젝트 구조

```
lookup-docker/
├── docker-compose.yml       # 전체 인프라 조립 설명서
├── .env                     # 환경 변수 (Git 제외)
├── .env.example             # 환경 변수 템플릿
├── .windsurfrules           # AI 코딩 가이드
├── README.md                # 프로젝트 문서 (본 파일)
├── .gitignore               # Git 제외 파일 목록
│
├── backend/                 # API 서버 및 DB 마이그레이션
│   ├── Dockerfile
│   ├── pyproject.toml       # uv 의존성 관리
│   ├── alembic/             # DB 마이그레이션 스크립트
│   └── app/                 # FastAPI 애플리케이션
│
├── crawler/                 # Playwright 기반 크롤링 엔진
│   ├── Dockerfile
│   ├── pyproject.toml       # uv 의존성 관리
│   └── workers/             # 크롤링 워커
│
├── frontend/                # 웹 서비스
│   ├── Dockerfile
│   └── src/                 # 프론트엔드 소스
│
└── postgres_data/           # DB 데이터 보관 (Git 제외)
```

---

## 🚀 시작하기

### 사전 요구사항
- Docker & Docker Compose
- Python 3.12+ (로컬 개발 시)
- uv 패키지 매니저

### 설치 및 실행

1. **저장소 클론**
```bash
git clone <repository-url>
cd lookup-docker
```

2. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

3. **Docker Compose로 전체 스택 실행**
```bash
docker-compose up -d
```

4. **서비스 확인**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (컨테이너 내부)
- PostgreSQL: localhost:5432

5. **로그 확인**
```bash
docker-compose logs -f [service-name]
# 예: docker-compose logs -f crawler
```

6. **서비스 중지**
```bash
docker-compose down
```

---

## 🔐 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 다음 값들을 설정하세요:

```bash
# Database
DB_USER=lookup_admin
DB_PASSWORD=your_secure_password  # 강력한 비밀번호로 변경
DB_NAME=lookup_db
DB_HOST=db                         # Docker 네트워크 내 서비스명
DB_PORT=5432

# API
BACKEND_URL=http://backend:8000    # Docker 네트워크 내 서비스명
```

⚠️ **중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

---

## 🏗 아키텍처

### 서비스 구성

```
┌─────────────┐
│  Frontend   │ :3000
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │ :8000 (internal)
│  (FastAPI)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│  PostgreSQL │◄─────┤   Crawler   │
│     :5432   │      │  (Workers)  │
└─────────────┘      └─────────────┘
```

### Docker 네트워크
- 모든 서비스는 `lookup_network` 브리지 네트워크로 연결
- 컨테이너 간 통신 시 서비스 이름을 호스트명으로 사용 (예: `db`, `backend`)
- 외부 접근은 포트 매핑을 통해서만 가능

---

## 🗄 데이터베이스 설계

### 핵심 원칙

1. **Primary Key**: 모든 테이블은 **UUID v7** 사용
   - 시간순 정렬 보장
   - 분산 환경에서 충돌 방지

2. **식별자 구분**
   - `styleNo` (브랜드 품번): 플랫폼 간 동일 상품 매칭을 위한 글로벌 키
   - `goodsNo` (플랫폼 품번): 각 플랫폼 사이트 접속을 위한 입장권

3. **Unique 제약**
   - `platform_products` 테이블: `(platform_name, platform_code)` 쌍을 유니크 키로 설정

4. **마이그레이션**
   - Alembic을 통한 버전 관리
   - `backend` 서비스 컨테이너 실행 시점(Runtime)에 자동 수행

### 주요 테이블 (예상)

```sql
-- 플랫폼별 상품
platform_products (
  id UUID PRIMARY KEY,
  platform_name VARCHAR,
  platform_code VARCHAR,  -- goodsNo
  style_no VARCHAR,       -- styleNo (글로벌 키)
  UNIQUE(platform_name, platform_code)
)

-- 가격 이력
price_history (
  id UUID PRIMARY KEY,
  product_id UUID REFERENCES platform_products(id),
  price INTEGER,
  created_at TIMESTAMP
)

-- 크롤링 작업 큐
crawl_jobs (
  id UUID PRIMARY KEY,
  job_type VARCHAR,       -- 'rank_crawl', 'detail_update'
  status VARCHAR,         -- 'pending', 'processing', 'completed', 'failed'
  payload JSONB,
  created_at TIMESTAMP
)
```

---

## 🕷 크롤링 파이프라인

### 3단계 계층 구조

```
1. Root Producer
   ↓ (카테고리/브랜드 목록 탐색)
   ↓ 생성: rank_crawl 티켓
   ↓
2. Semi-Producer
   ↓ (랭킹 페이지 탐색)
   ↓ 생성: detail_update 티켓
   ↓
3. Consumer (Worker)
   ↓ (상세 페이지 파싱)
   ↓ 저장: Price + Metadata
   ↓
   DB
```

### 작업 큐 관리

- **테이블**: `crawl_jobs`
- **상태 관리**: `pending` → `processing` → `completed` / `failed`
- **원자성 보장**: `UPDATE ... RETURNING *` 문법 사용

### 최적화 전략

1. **Lazy Update (지연된 업데이트)**
   - 상세 정보(Metadata)는 최초 수집 후 7~15일 주기로만 갱신
   - 가격 정보는 더 자주 업데이트

2. **데이터 다이어트**
   - SEO 정보, 사이트 설정값 등 불필요한 데이터 제거
   - 핵심 정보(소재, 태그, 리뷰 등)만 1~2KB 내외로 보관

3. **IP 차단 방지**
   - 적절한 요청 간격 설정
   - User-Agent 로테이션
   - 개발 시 로컬 HTML 파일 활용

---

## 💻 개발 가이드

### 로컬 개발 환경 설정

1. **uv 설치** (필수)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **의존성 설치**
```bash
cd backend
uv sync

cd ../crawler
uv sync
```

3. **새 패키지 추가**
```bash
uv add <package-name>
```

### 개발 워크플로우

1. **IP 차단 방지를 위한 개발 방법**
   ```python
   # 1단계: Playwright로 HTML 저장
   html = await page.content()
   with open('local.html', 'w') as f:
       f.write(html)
   
   # 2단계: BeautifulSoup4로 오프라인 파싱 로직 개발
   with open('local.html', 'r') as f:
       soup = BeautifulSoup(f.read(), 'html.parser')
   ```

2. **코드 스타일**
   - 모든 함수에 Docstring 작성
   - 타입 힌트 명시
   - 변수명은 명확하고 의미 있게

3. **DB 쿼리 작성**
   ```python
   # 작업 큐 원자성 보장
   result = await conn.execute(
       """
       UPDATE crawl_jobs
       SET status = 'processing'
       WHERE id = (
           SELECT id FROM crawl_jobs
           WHERE status = 'pending'
           ORDER BY created_at
           LIMIT 1
           FOR UPDATE SKIP LOCKED
       )
       RETURNING *
       """
   )
   ```

### Docker 개발 팁

```bash
# 특정 서비스만 재빌드
docker-compose up -d --build backend

# 컨테이너 내부 접속
docker exec -it lookup_backend bash

# 로그 실시간 확인
docker-compose logs -f crawler

# 볼륨 초기화 (주의: 데이터 삭제됨)
docker-compose down -v
```

---

## 🔒 보안 및 주의사항

### 필수 보안 수칙

1. **환경 변수 관리**
   - ❌ `.env` 파일을 Git에 커밋하지 않기
   - ✅ `.env.example`로 필요한 변수 목록만 공유
   - ✅ 강력한 비밀번호 사용

2. **SSH 터널링**
   - 프로덕션 DB 접속 시 SSH 터널 사용
   - 직접 포트 노출 금지

3. **API 키 관리**
   - 환경 변수로 관리
   - 코드에 하드코딩 금지

### 크롤링 에티켓

1. **요청 간격 준수**
   - 과도한 요청으로 서버에 부하 주지 않기
   - robots.txt 확인

2. **개발 시 주의사항**
   - 로컬 HTML 파일로 파싱 로직 개발
   - 완성 후에만 실제 크롤링 테스트

---

## 📚 참고 자료

- [uv 공식 문서](https://github.com/astral-sh/uv)
- [Playwright Python](https://playwright.dev/python/)
- [PostgreSQL 16 문서](https://www.postgresql.org/docs/16/)
- [Docker Compose 문서](https://docs.docker.com/compose/)

---

## 📝 라이선스

TBD

---

## 👥 기여하기

TBD

---

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ by LookUp Team**
