from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routes import user  # 방금 만든 user 라우터 불러오기

# DB 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ★ 핵심: 쪼개놓은 라우터를 여기서 합침!
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"status": "서버 정상 작동 중"}
