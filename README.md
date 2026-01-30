# Health Kiosk Backend (API Server)

이 프로젝트는 사용자 건강 맞춤형 메뉴 추천 키오스크를 위한 백엔드 API 서버입니다.
FastAPI를 기반으로 구축되었으며, 얼굴 인식을 통한 로그인, 사용자 건강 설문 데이터 처리, 그리고 Google Gemini AI를 활용한 맞춤형 식단 추천 기능을 제공합니다.

## 🔗 관련 리포지토리 (Repositories)
이 프로젝트는 프론트엔드와 백엔드로 나뉘어 있습니다.
* **Frontend**: [health_kiosk_front 링크 바로가기](https://github.com/rkddlsxo/health_kiosk_front)
* **Backend**: [health_kiosk_back 링크 바로가기](https://github.com/rkddlsxo/health_kiosk_back)

## 👥 팀원 및 역할 (Team)
| 이름 | 역할 | GitHub | 담당 기능 |
|:---:|:---:|:---:|:---|
| **강인태** | Full Stack | [@rkddlsxo](https://github.com/rkddlsxo) | 프론트엔드, 백엔드 , AI요약 기능 |
| **김지웅** | Frontend | [@moongyuxx]([링크](https://github.com/wldnd7145)) | 백엔드, AI기능 전반 |
| **문규원** | Backend | [@wldnd7145]([링크](https://github.com/moongyuxx)) | API 설계, 문서, UI/UX 디자인, 백엔드|


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
