from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, database

# DB 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. 이미 있는 아이디인지 확인
    existing_user = db.query(models.User).filter(models.User.account_id == user.account_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    
    # 2. 없으면 저장
    new_user = models.User(
        account_id=user.account_id,
        password=user.password,
        name=user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user