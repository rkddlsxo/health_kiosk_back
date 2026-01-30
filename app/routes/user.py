from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from .. import models, schemas, database

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
    
    return {"message": "Login successful", "name": db_user.name,"account_id": db_user.account_id}

@router.put("/{account_id}/health-info")
def update_health_info(account_id: str, info: schemas.HealthRecordCreate, db: Session = Depends(database.get_db)):
    # 1. 유저 찾기
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. 기존 건강 기록이 있는지 확인 (있으면 업데이트, 없으면 생성)
    #    여기서는 단순하게 가장 최근 기록을 가져오거나 새로 만듭니다.
    health_record = db.query(models.UserHealth).filter(models.UserHealth.user_id == user.id).first()
    
    if not health_record:
        health_record = models.UserHealth(user_id=user.id)
        db.add(health_record)
    
    # 3. 데이터 맵핑 (스키마 -> DB 모델)
    #    입력된 값들만 업데이트합니다.
    data_dict = info.dict(exclude_unset=True) # 입력 안 된 건 건너뜀
    for key, value in data_dict.items():
        if hasattr(health_record, key):
            setattr(health_record, key, value)
    
    # 검진일이 없으면 오늘 날짜로
    if not health_record.checkup_date:
        health_record.checkup_date = date.today()

    db.commit()
    return {"message": "건강 정보가 저장되었습니다."}

@router.post("/{account_id}/allergies")
def add_allergy(account_id: str, allergy: schemas.AllergyCreate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_allergy = models.UserAllergy(
        user_id=user.id,
        allergen_name=allergy.allergen_name,
        reaction=allergy.reaction,
        severity=allergy.severity
    )
    db.add(new_allergy)
    db.commit()
    return {"message": "알레르기 정보가 추가되었습니다."}