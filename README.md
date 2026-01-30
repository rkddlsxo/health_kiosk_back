# 건강 맞춤형 카페 키오스크 백엔드

✅ **검증 완료: 2026-01-30**

## 시스템 구성

- **프레임워크**: FastAPI
- **데이터베이스**: MySQL (kiosk)
- **언어**: Python 3.10

## API 엔드포인트

### 사용자 관리
- `POST /user/register` - 회원가입
- `POST /user/login` - 로그인

### 건강 정보
- `PUT /user/{account_id}/health-info` - 건강검진 정보 등록/수정
- `POST /user/{account_id}/allergies` - 알러지 정보 추가

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install pymysql

# MySQL 설정
# database.py에서 연결 정보 확인: mysql+pymysql://root:1234@localhost:3306/kiosk

# 서버 실행
uvicorn app.main:app --reload
```

## 테스트

```bash
# 전체 시스템 통합 테스트
python scripts\test_full_flow.py
```

## API 문서
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
