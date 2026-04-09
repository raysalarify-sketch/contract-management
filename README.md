# 워크드 안전거래 플랫폼

보증보험 대리점 라이센스 기반의 B2B2C 주택 안전거래 플랫폼

## 아키텍처

```
Frontend (React)  ──→  Django REST API  ──→  PostgreSQL
                            │
                       Celery Worker  ──→  Redis
                            │
                     알림톡 / 전자서명 / 보증보험 API
```

## 전체 플로우 (12단계)

```
매물 지도 → 임대인 문의 → 리스크 스캔 → 판정 → 안전장치 → 계약하기
    → 계약서 → 중개사 확인 → 전자서명 → 월세 스케줄 → 상호 리뷰 → 사후관리
```

## 프로젝트 구조

```
workd-project/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── workd_project/        # Django 설정
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/              # 사용자 (임대인/임차인/중개사)
│   │   ├── models.py          # User, Company, LandlordProfile, AgentProfile
│   │   └── urls.py            # JWT 인증
│   ├── properties/            # 매물 + 리스크 스캔
│   │   ├── models.py          # Property, RiskScan, PropertyTag
│   │   └── views.py           # 매물 CRUD, 보험가능 지도, 스캔 실행
│   ├── contracts/             # 문의 → 합의 → 계약 → 서명
│   │   ├── models.py          # Inquiry, ContractAgreement, Contract, ESignature
│   │   └── views.py           # 문의, 합의, 서명, 사후관리 API
│   ├── insurance/             # 보증보험 / 공증 / 근저당
│   │   └── models.py          # InsuranceApplication, NotaryApplication, MortgageApplication
│   ├── reviews/               # 상호 리뷰
│   │   └── models.py          # Review (임대인↔임차인)
│   └── schedules/             # 월세 스케줄 + 사후관리
│       └── models.py          # RentSchedule, ContractEvent, Notification
└── frontend/
    └── src/
```

## DB 모델 관계도

```
Company ──1:N──→ User (직원)
User ──1:N──→ Property (임대인 매물)
User ──1:1──→ LandlordProfile / AgentProfile

Property ──1:N──→ RiskScan (스캔 이력)
Property ──1:N──→ Inquiry (문의)
Property ──1:N──→ PropertyTag

Inquiry ──1:N──→ InquiryMessage (채팅)

Property ──→ ContractAgreement (합의) ──→ Contract (계약서)
Contract ──1:N──→ ESignature (전자서명, 최대 3건)
Contract ──1:1──→ AgentVerification (중개사 확인)
Contract ──1:N──→ InsuranceApplication (보증보험)
Contract ──1:N──→ NotaryApplication (공증)
Contract ──1:N──→ MortgageApplication (근저당)
Contract ──1:N──→ RentSchedule (월세 스케줄)
Contract ──1:N──→ ContractEvent (사후관리 이벤트)
Contract ──1:N──→ Review (상호 리뷰)
User ──1:N──→ Notification (알림)
```

## API 엔드포인트

### 인증
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /api/v1/accounts/token/ | 로그인 (JWT) |
| POST | /api/v1/accounts/token/refresh/ | 토큰 갱신 |

### 매물
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/v1/properties/ | 매물 리스트 (필터/검색) |
| GET | /api/v1/properties/insurable-map/ | 보증보험 가능 매물 지도 |
| GET | /api/v1/properties/{id}/ | 매물 상세 |
| POST | /api/v1/properties/{id}/scan/ | 리스크 스캔 실행 |
| GET | /api/v1/properties/{id}/reviews/ | 임대인 리뷰 조회 |

### 계약
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /api/v1/contracts/inquiries/ | 문의 생성 |
| POST | /api/v1/contracts/inquiries/{id}/send-message/ | 메시지 전송 |
| POST | /api/v1/contracts/inquiries/{id}/schedule-viewing/ | 방문 일정 |
| POST | /api/v1/contracts/agreements/ | 계약 합의 생성 |
| POST | /api/v1/contracts/agreements/{id}/agree/ | 동의 |
| POST | /api/v1/contracts/{id}/confirm/ | 계약서 확인 |
| POST | /api/v1/contracts/{id}/agent-verify/ | 중개사 확인 |
| POST | /api/v1/contracts/{id}/sign/ | 전자서명 |
| GET | /api/v1/contracts/{id}/post-management/ | 사후관리 |

## 실행 방법

### Docker (권장)
```bash
git clone <repo>
cd workd-project
docker compose up -d
```
→ Backend: http://localhost:8000
→ Frontend: http://localhost:3000

### 로컬 개발
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (별도 터미널)
cd frontend
npm install
npm run dev
```

## 환경변수 (.env)

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=workd_db
DB_USER=workd_user
DB_PASSWORD=workd_pass
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
KAKAO_API_KEY=your-kakao-key
KAKAO_SENDER_KEY=your-sender-key
CORS_ORIGINS=http://localhost:3000
```

## 다음 단계 (TODO)

### Phase 1 - MVP
- [ ] 등기부등본 API 연동 (코리아크레딧뷰로 등)
- [ ] 전자서명 서비스 연동 (카카오 인증서 등)
- [ ] 알림톡 발송 연동 (카카오 비즈메시지)
- [ ] 보증보험 API 연동 (HUG/SGI)

### Phase 2 - 확장
- [ ] 프론트엔드 React 앱 완성 (프로토타입 → 실서비스)
- [ ] 실시간 채팅 (WebSocket / Django Channels)
- [ ] 결제 연동 (보험료, 공증비, 근저당 설정비)
- [ ] 포티투닷 연동 (인사정보 ↔ 대출정보)

### Phase 3 - 고도화
- [ ] AI 기반 리스크 판정 모델
- [ ] 시세 모니터링 자동화
- [ ] 계약서 OCR / 자동 검증
- [ ] 모바일 앱 (React Native)
