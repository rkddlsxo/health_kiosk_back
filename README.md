# Medi-Pass Backend (API Server)

이 프로젝트는 사용자 건강 맞춤형 메뉴 추천 키오스크를 위한 백엔드 API 서버입니다.
FastAPI를 기반으로 구축되었으며, 얼굴 인식을 통한 로그인, 사용자 건강 설문 데이터 처리, 그리고 Google Gemini AI를 활용한 맞춤형 식단 추천 기능을 제공합니다.

## 🔗 관련 리포지토리 (Repositories)
이 프로젝트는 프론트엔드와 백엔드로 나뉘어 있습니다.
* **Frontend**: [health_kiosk_front 링크 바로가기](https://github.com/rkddlsxo/health_kiosk_front)
* **Backend**: [health_kiosk_back 링크 바로가기](https://github.com/rkddlsxo/health_kiosk_back)

## 👥 팀원 및 역할 (Team)
| 이름 | 역할 | GitHub | 담당 기능 |
|:---:|:---:|:---:|:---|
| **강인태** | 팀장 | [@rkddlsxo](https://github.com/rkddlsxo) | 프론트엔드, 백엔드 , AI요약 기능 |
| **김지웅** | 팀원 | [@wldnd7145](https://github.com/wldnd7145) | AI기능 전반, 백엔드 |
| **문규원** | 팀원 | [@moongyuxx](https://github.com/moongyuxx) | API 설계, 문서, UI/UX 디자인, 백엔드|


## 🛠 기술 스택 (Tech Stack)

* **Language**: Python 3.9+
* **Framework**: FastAPI
* **Database**: MySQL (SQLAlchemy ORM)
* **AI & ML**: 
    * `face_recognition` (얼굴 인식 및 임베딩 추출)
    * Google Gemini Pro Vision / Flash (식단 추천 및 이미지 분석)
* **Authentication**: JWT, Face Auth

## 📂 프로젝트 구조 (Structure)

```text
health_kiosk_back/
├── app/
│   ├── api/            # API 라우터 (auth, users, menu, kiosk, recommendation)
│   ├── models.py       # 데이터베이스 모델 (SQLAlchemy)
│   ├── schemas.py      # Pydantic 스키마 (데이터 검증)
│   ├── services/       # 비즈니스 로직 (Face Service, Gemini Service)
│   └── database.py     # DB 연결 설정
├── scripts/            # 초기 데이터 시딩 및 테스트 스크립트
├── .env                # 환경 변수 (Github에 업로드 금지)
└── requirements.txt    # 의존성 패키지 목록

```
### 🚀 설치 및 실행 방법 (Installation & Run)

```Bash
1. 환경 설정
Python 가상환경을 생성하고 활성화합니다.

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate
# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate
2. 패키지 설치
필요한 라이브러리를 설치합니다. (dlib 설치 시 CMake가 필요할 수 있습니다.)

pip install -r requirements.txt
3. 환경 변수 설정 (.env)
루트 경로에 .env 파일을 생성하고 다음 내용을 채워주세요.

Ini, TOML
DATABASE_URL=mysql+pymysql://사용자:비밀번호@localhost:3306/health_kiosk
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your_google_gemini_api_key
4. 데이터베이스 초기화
MySQL 서버가 실행 중이어야 합니다. 아래 스크립트로 테이블을 생성하고 기초 메뉴 데이터를 넣습니다.

# 테이블 생성 및 초기화
python scripts/init_mysql_data.py
python scripts/init_menu_data.py
5. 서버 실행
Uvicorn을 사용하여 서버를 실행합니다.

uvicorn app.main:app --reload
서버는 기본적으로 http://127.0.0.1:8000 에서 실행됩니다.

```
### 📝 주요 API 기능
Auth: 회원가입, 로그인 (ID/PW), 얼굴 로그인

User: 사용자 정보 조회, 건강 설문 정보 등록/수정

Menu: 메뉴 목록 조회, 메뉴 상세 정보

Recommendation: 사용자 건강 정보(알러지, 질환) 기반 Gemini AI 메뉴 추천

## 📊 데이터 모델 설계 (Data Schema)

### 1. 사용자 및 인증 (User & Auth)
| 구분 | 클래스명 | 주요 필드 | 설명 |
| :--- | :--- | :--- | :--- |
| **Request** | `UserCreate` | `account_id`, `password`, `name` | 회원가입 요청 데이터 |
| **Request** | `LoginRequest` | `account_id`, `password` | 로그인 요청 데이터 |
| **Response** | `LoginResponse` | `success`, `message`, `user_id`, `user_name` | 로그인 성공 결과 및 유저 정보 |

### 2. 건강 및 알러지 (Health & Allergy)
| 구분 | 클래스명 | 주요 필드 | 설명 |
| :--- | :--- | :--- | :--- |
| **Request** | `UserHealthCreate` | `height`, `weight`, `bp_high`, `fasting_blood_sugar` 등 | 건강검진 데이터 수동 입력 |
| **Response** | `UserHealthResponse` | `id`, `user_id`, `bmi`, `ast`, `alt` 등 | 등록된 건강 데이터 조회 |
| **Request** | `UserAllergyCreate` | `allergen_name`, `reaction`, `severity` | 알러지 유발 물질 및 증상 등록 |

---

## 🔌 API 명세 (API Specification)

### 1. 유저 및 인증 (User & Auth)
| 기능 | 메서드 | 엔드포인트 | 설명 |
| :--- | :---: | :--- | :--- |
| 회원가입 | `POST` | `/api/users/register` | 일반 계정 회원가입 |
| 로그인 | `POST` | `/api/users/login` | 계정 ID/PW 기반 로그인 |
| 로그아웃 | `POST` | `/api/users/logout` | 세션 종료 및 키오스크 로그아웃 |
| 얼굴 등록 | `POST` | `/api/users/{account_id}/face` | 사진 업로드 및 얼굴 임베딩 저장 |
| 사용자 조회 | `GET` | `/api/users/{account_id}` | 메인 화면용 유저 프로필 조회 |

### 2. 건강 데이터 자동/수동 등록 (Health Data)
| 기능 | 메서드 | 엔드포인트 | 설명 |
| :--- | :---: | :--- | :--- |
| 건강검진 스캔 | `POST` | `/api/users/{id}/health/scan` | **AI OCR**: 검진표 이미지 자동 분석 및 저장 |
| 알레르기 스캔 | `POST` | `/api/users/{id}/allergies/scan` | **AI OCR**: 알레르기 서류 자동 분석 및 저장 |
| 건강정보 등록/수정 | `POST`/`PUT` | `/api/users/{id}/health` | 건강 데이터 직접 입력 및 업데이트 |
| 알레르기 등록 | `POST` | `/api/users/{id}/allergies` | 알러지 정보 직접 입력 |

### 3. 키오스크 및 AI 기능 (Kiosk & AI)
| 기능 | 메서드 | 엔드포인트 | 설명 |
| :--- | :---: | :--- | :--- |
| 키오스크 얼굴 인증 | `POST` | `/api/kiosk/detect-face` | 키오스크 카메라를 통한 실시간 인증 |
| 메뉴 데이터 조회 | `GET` | `/api/menus` | 전체 키오스크 메뉴 목록 불러오기 |
| AI 메뉴 추천 | `POST` | `/api/recommend/menu` | **Gemini**: 사용자 맞춤형 식단 큐레이션 |


## ERD

```mermaid
erDiagram
    USER ||--o{ HEALTH_RECORD : "records"
    USER ||--o{ ALLERGY : "has"
    USER ||--o| FACE_EMBEDDING : "registers"
    
    USER {
        int id PK
        string account_id
        string password
        string name
        datetime created_at
    }

    HEALTH_RECORD {
        int id PK
        int user_id FK
        date checkup_date
        float height
        float weight
        float bmi
        int bp_high
        int bp_low
        int fasting_blood_sugar
        int total_cholesterol
    }

    ALLERGY {
        int id PK
        int user_id FK
        string allergen_name
        string reaction
        string severity
    }

    FACE_EMBEDDING {
        int id PK
        int user_id FK
        string image_path
        string embedding_data
    }

    MENU {
        int id PK
        string name
        int calories
        string category
        int price
    }
```

User (사용자): 시스템의 중심 엔티티입니다. account_id로 식별하며, 여러 개의 건강 기록과 알러지 정보를 가질 수 있습니다.

Health_Record (건강 검진): 사용자의 신체 수치를 저장합니다. (1:N 관계) 시간의 흐름에 따른 건강 변화를 추적하기 위해 여러 레코드를 가질 수 있도록 설계되었습니다.

Allergy (알러지): 사용자가 가진 알러지 유발 물질들을 저장합니다. (1:N 관계)

Face_Embedding (얼굴 데이터): 얼굴 인식 로그인을 위해 추출된 수치화된 벡터 데이터를 저장합니다.

Menu (메뉴): 추천의 대상이 되는 음식 데이터입니다. Gemini AI가 사용자의 Health_Record 및 Allergy와 비교하여 최적의 메뉴를 선별합니다.
