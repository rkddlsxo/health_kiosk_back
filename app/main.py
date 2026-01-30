from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routes import user
from .api import auth, menu, health, recommendation, kiosk, users

# DB 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user.router)  # /user/*
app.include_router(auth.router)  # /api/auth/*
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])  # /api/menu/*
app.include_router(health.router)  # /api/health/*
app.include_router(recommendation.router)  # /api/recommend/*
app.include_router(kiosk.router)  # /api/kiosk/*
app.include_router(users.router, prefix="/api/users") # /api/users/* (프론트엔드 호환용)

@app.get("/")
def read_root():
    return {"status": "서버 정상 작동 중"}
