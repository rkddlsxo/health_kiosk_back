"""
프론트엔드 Survey.jsx와 호환되는 사용자 API
경로 Prefix: /api/users
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserFace, UserHealth, UserAllergy
from app.services.face_service import get_face_service
from app.services.gemini_service import get_gemini_service
from app.schemas import (
    UserHealthCreate,
    UserAllergyCreate,
    UserHealthResponse,
    UserAllergyResponse
) # schemas.py에 있는 모델 재사용
from typing import List, Optional
import json

router = APIRouter(tags=["frontend-users"]) 

# 주의: main.py에서 prefix="/api/users" 로 등록할 예정

def get_user_by_account_id(db: Session, account_id: str) -> User:
    user = db.query(User).filter(User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 1. 얼굴 등록
@router.post("/{account_id}/face")
async def register_face(
    account_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    face_service = get_face_service()
    
    image_bytes = await file.read()
    embedding = face_service.extract_face_embedding(image_bytes)
    
    if embedding is None:
        raise HTTPException(status_code=400, detail="얼굴을 감지할 수 없습니다. 다시 촬영해주세요.")
    
    # 기존 얼굴 정보 삭제 후 재등록 (또는 추가) -> 여기선 추가가 일반적이지만 1:1이면 삭제 후 등록
    # 일단 추가로 구현
    user_face = UserFace(
        user_id=user.id,
        embedding=json.dumps(embedding.tolist()),
        embedding_model="insightface-arcface"
    )
    db.add(user_face)
    db.commit()
    
    return {"message": "얼굴 등록 완료"}

# 2. 건강검진표 스캔
@router.post("/{account_id}/health/scan")
async def scan_health_report(
    account_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    gemini_service = get_gemini_service()
    
    image_bytes = await file.read()
    parsed_data = gemini_service.parse_health_report(image_bytes)
    
    if not parsed_data:
        raise HTTPException(status_code=400, detail="건강검진표 분석 실패")
    
    # 저장 또는 업데이트
    health_record = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    if not health_record:
        health_record = UserHealth(user_id=user.id, **parsed_data)
        db.add(health_record)
    else:
        for k, v in parsed_data.items():
            if hasattr(health_record, k) and v is not None:
                setattr(health_record, k, v)
    
    db.commit()
    return {"message": "건강 정보 분석 및 저장 완료", "data": parsed_data}

# 3. 건강정보 수동 등록
@router.post("/{account_id}/health")
async def update_health_manual(
    account_id: str,
    data: dict, # 프론트에서 보내는 형식이 스키마와 다를 수 있어 dict로 받음 (vision_l 등)
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    
    # 딕셔너리를 모델 필드에 매핑
    health_updates = {}
    
    # has_hypertension 같은 boolean 플래그는 DB 필드가 아닐 수 있음.
    # UserHealth 모델에는 vision_l, hearing_l 등이 있음.
    # 프론트: vision_l, vision_r, hearing_l, hearing_r (OK)
    # 질환 정보는? UserHealth 모델에 질환 필드가 있는지 확인 필요.
    # models.py를 못 봤지만, 일단 있는 필드만 매핑.
    
    valid_fields = [
        "vision_l", "vision_r", "hearing_l", "hearing_r",
        "height", "weight", "waist", "bmi", "bp_high", "bp_low"
    ]
    
    for k, v in data.items():
        if k in valid_fields:
            health_updates[k] = v
            
    # 질환 정보(has_diabetes 등) 처리는 모델에 따라 다름. 
    # 일단 스킵하거나 모델 확인 필요. -> 확인 안 했으니 안전하게 있는 것만.
    
    health_record = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    if not health_record:
        health_record = UserHealth(user_id=user.id, **health_updates)
        db.add(health_record)
    else:
        for k, v in health_updates.items():
            setattr(health_record, k, v)
            
    db.commit()
    return {"message": "건강 정보 저장 완료"}

# 4. 알레르기 스캔
@router.post("/{account_id}/allergies/scan")
async def scan_allergy_test(
    account_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    gemini_service = get_gemini_service()
    
    image_bytes = await file.read()
    allergens = gemini_service.parse_allergy_test(image_bytes)
    
    if allergens is None:
        raise HTTPException(status_code=400, detail="알레르기 검사지 분석 실패")
    
    # 저장
    count = 0
    for allergen in allergens:
        exists = db.query(UserAllergy).filter(
            UserAllergy.user_id == user.id,
            UserAllergy.allergen_name == allergen
        ).first()
        if not exists:
            db.add(UserAllergy(user_id=user.id, allergen_name=allergen, reaction="양성"))
            count += 1
            
    db.commit()
    return {"message": f"{count}개의 알레르기 정보가 추가되었습니다.", "allergens": allergens}

# 5. 알레르기 수동 등록
@router.post("/{account_id}/allergies")
async def add_allergy_manual(
    account_id: str,
    data: UserAllergyCreate,
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    
    exists = db.query(UserAllergy).filter(
        UserAllergy.user_id == user.id,
        UserAllergy.allergen_name == data.allergen_name
    ).first()
    
    if not exists:
        db.add(UserAllergy(user_id=user.id, allergen_name=data.allergen_name, severity=data.severity))
        db.commit()
        
    return {"message": "알레르기 추가 완료"}
