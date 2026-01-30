from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database  # ..은 상위 폴더를 의미

# API 라우터 생성 (prefix를 달면 주소 앞에 자동으로 붙음)
router = APIRouter(
    prefix="/user",
    tags=["User"]  # Swagger 문서에서 섹션을 나눠줌
)

# 회원가입 (주소: POST /user/register)
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.account_id == user.account_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    
    new_user = models.User(
        account_id=user.account_id,
        password=user.password,
        name=user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 로그인 (주소: POST /user/login)
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.account_id == user.account_id).first()
    
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")
    
    return {"message": "Login successful", "name": db_user.name}