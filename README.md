# 건강 맞춤형 카페 키오스크 백엔드

얼굴 인식 로그인과 건강 프로필 기반 맞춤형 메뉴 추천을 제공하는 카페 키오스크 백엔드 API입니다.

## 주요 기능

- **얼굴 인식 로그인**: InsightFace를 사용한 빠르고 정확한 얼굴 인식
- **건강정보 관리**: Gemini API를 활용한 건강검진표 자동 파싱
- **맞춤형 메뉴 추천**: 사용자의 건강 상태와 알러지 정보 기반 메뉴 필터링
- **대체 옵션 제안**: 건강에 좋지 않은 메뉴에 대한 스마트한 대체 제안

## 기술 스택

- **Backend**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Face Recognition**: InsightFace (ArcFace 512차원 임베딩)
- **AI**: Google Gemini 1.5 Flash

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example`을 `.env`로 복사하고 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```
DATABASE_URL=sqlite:///./health_kiosk.db
GEMINI_API_KEY=your_gemini_api_key_here  # 필수!
SECRET_KEY=your_secret_key_here
FACE_SIMILARITY_THRESHOLD=0.5
```

### 4. Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. "Get API key" 클릭
3. API 키 복사 → `.env` 파일에 입력

### 5. 메뉴 시드 데이터 생성

```bash
python scripts/seed_menu_data.py
```

### 6. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버 실행 후: http://localhost:8000

## API 문서

FastAPI Swagger UI: http://localhost:8000/docs

### 주요 엔드포인트

#### 인증
- `POST /api/auth/register` - 회원가입 (이름, 전화번호, 얼굴 사진)
- `POST /api/auth/login/face` - 얼굴 인식 로그인
- `GET /api/auth/users/{user_id}` - 사용자 정보 조회

#### 건강정보
- `POST /api/health/users/{user_id}/health-report` - 건강검진표 이미지 업로드 (자동 파싱)
- `POST /api/health/users/{user_id}/health-profile` - 건강 프로필 직접 입력/수정
- `GET /api/health/users/{user_id}/health-profile` - 건강 프로필 조회
- `POST /api/health/users/{user_id}/allergy` - 알러지 정보 등록/수정
- `GET /api/health/users/{user_id}/allergy` - 알러지 정보 조회

#### 메뉴
- `GET /api/menus` - 전체 메뉴 조회
- `GET /api/menus/{menu_id}` - 특정 메뉴 상세
- `GET /api/menus/{menu_id}/options` - 메뉴 옵션 조회

#### 추천
- `GET /api/recommend/{user_id}` - 사용자 맞춤 메뉴 추천

## 프로젝트 구조

```
health_kiosk_back/
├── app/
│   ├── api/              # API 라우터
│   │   ├── auth.py       # 인증 관련
│   │   ├── health.py     # 건강정보 관련
│   │   ├── menu.py       # 메뉴 관련
│   │   └── recommendation.py  # 추천 관련
│   ├── models/           # 데이터베이스 모델
│   │   ├── user.py
│   │   ├── health.py
│   │   └── menu.py
│   ├── schemas/          # Pydantic 스키마
│   ├── services/         # 비즈니스 로직
│   │   ├── face_service.py    # 얼굴 인식
│   │   └── gemini_service.py  # Gemini API
│   ├── config.py         # 설정 관리
│   ├── database.py       # DB 연결
│   └── main.py           # FastAPI 앱
├── scripts/              # 유틸리티 스크립트
│   └── seed_menu_data.py # 메뉴 시드 데이터
├── requirements.txt      # Python 의존성
├── .env.example          # 환경변수 예시
└── README.md
```

## 사용 예시

### 1. 회원가입 + 얼굴 등록

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -F "name=홍길동" \
  -F "phone=01012345678" \
  -F "face_image=@face.jpg"
```

### 2. 건강검진표 업로드

```bash
curl -X POST "http://localhost:8000/api/health/users/1/health-report" \
  -F "report_image=@checkup.jpg"
```

### 3. 알러지 정보 등록

```bash
curl -X POST "http://localhost:8000/api/health/users/1/allergy" \
  -H "Content-Type: application/json" \
  -d '{"allergens": ["milk", "nuts"]}'
```

### 4. 얼굴 로그인

```bash
curl -X POST "http://localhost:8000/api/auth/login/face" \
  -F "face_image=@face2.jpg"
```

### 5. 맞춤 메뉴 추천 받기

```bash
curl "http://localhost:8000/api/recommend/1"
```

## 건강 기반 필터링 규칙

Gemini AI가 다음 규칙에 따라 메뉴를 평가합니다:

- **알러지 성분 포함**: 해당 메뉴 차단
- **혈당 높음 (≥100 mg/dL)**: 당분 많은 메뉴 경고
- **LDL 콜레스테롤 높음 (≥130 mg/dL)**: 포화지방 많은 메뉴 경고
- **중성지방 높음 (≥150 mg/dL)**: 지방 많은 메뉴 경고
- **혈압 높음 (≥130/85 mmHg)**: 카페인 많은 메뉴 경고

경고 메뉴에 대해서는 자동으로 대체 옵션(저지방 우유, 무가당 등)을 제안합니다.

## 라이선스

MIT License
