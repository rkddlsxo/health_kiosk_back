from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import get_settings

# 모델 임포트 (테이블 생성을 위해 필요)
from app.models import User, UserFace, UserHealth, UserAllergy, Menu, MenuOption

settings = get_settings()

# FastAPI 앱 생성
app = FastAPI(
    title="Health Kiosk Backend",
    description="건강 맞춤형 카페 키오스크 백엔드 API",
    version="1.0.0",
    debug=settings.debug
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경, 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    """헬스 체크 엔드포인트"""
    return {
        "message": "Health Kiosk Backend API is running!",
        "version": "1.0.0",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    """상태 체크"""
    return {"status": "healthy"}


# 라우터 등록
from app.api import auth, health, menu, recommendation

app.include_router(auth.router, tags=["인증"])
app.include_router(health.router, tags=["건강정보"])
app.include_router(menu.router, tags=["메뉴"])
app.include_router(recommendation.router, tags=["추천"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
