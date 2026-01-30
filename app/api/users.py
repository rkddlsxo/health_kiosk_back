"""
프론트엔드 Survey.jsx와 호환되는 사용자 API
경로 Prefix: /api/users
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserFace, UserHealth, UserAllergy
from app.services.face_service import get_face_service
from app.services.gemini_service import get_gemini_service
from app.services.recommendation_service import update_user_recommendation
from app.schemas import (
    UserHealthCreate,
    UserAllergyCreate,
    UserHealthResponse,
    UserAllergyResponse
) 
from typing import List, Optional
import json

router = APIRouter(tags=["frontend-users"]) 

def get_user_by_account_id(db: Session, account_id: str) -> User:
    user = db.query(User).filter(User.account_id == account_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 1. 얼굴 등록
@router.post("/{account_id}/face")
async def register_face(
    account_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    face_service = get_face_service()
    
    image_bytes = await file.read()
    embedding = face_service.extract_face_embedding(image_bytes)
    
    if embedding is None:
        raise HTTPException(status_code=400, detail="얼굴을 감지할 수 없습니다. 다시 촬영해주세요.")
    
    user_face = UserFace(
        user_id=user.id,
        embedding=json.dumps(embedding.tolist()),
        embedding_model="insightface-arcface"
    )
    db.add(user_face)
    db.commit()
    
    # [Async] 얼굴 등록 완료 시점에도 추천 데이터 갱신 (마지막 단계)
    # db 세션은 넘기지 않음 (서비스 내부에서 새 세션 생성)
    background_tasks.add_task(update_user_recommendation, user.id)
    
    return {"message": "얼굴 등록 완료"}

# 2. 건강검진표 스캔
@router.post("/{account_id}/health/scan")
async def scan_health_report(
    account_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    gemini_service = get_gemini_service()
    
    image_bytes = await file.read()
    parsed_data = gemini_service.parse_health_report(image_bytes)
    
    
    # 분석 실패 시(빈 딕셔너리) 400 에러 대신 빈 데이터로 진행 (수동 입력 유도)
    if parsed_data is None:
        parsed_data = {}
        # raise HTTPException(status_code=400, detail="건강검진표 분석 실패")
    
    health_record = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    if not health_record:
        # parsed_data가 비어있어도 생성
        health_record = UserHealth(user_id=user.id, **parsed_data)
        db.add(health_record)
    else:
        for k, v in parsed_data.items():
            if hasattr(health_record, k) and v is not None:
                setattr(health_record, k, v)
    
    db.commit()
    
    # [Async] 추천 데이터 갱신
    background_tasks.add_task(update_user_recommendation, user.id)
    
    return {"message": "건강 정보 분석 및 저장 완료. AI 추천 생성 중...", "data": parsed_data}

# 3. 건강정보 수동 등록
@router.post("/{account_id}/health")
async def update_health_manual(
    account_id: str,
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    
    health_updates = {}
    valid_fields = [
        "vision_l", "vision_r", "hearing_l", "hearing_r",
        "height", "weight", "waist", "bmi", "bp_high", "bp_low"
    ]
    
    for k, v in data.items():
        if k in valid_fields:
            health_updates[k] = v
    
    health_record = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    if not health_record:
        health_record = UserHealth(user_id=user.id, **health_updates)
        db.add(health_record)
    else:
        for k, v in health_updates.items():
            setattr(health_record, k, v)
            
    db.commit()
    
    # [Async] 추천 데이터 갱신
    background_tasks.add_task(update_user_recommendation, user.id)
    
    return {"message": "건강 정보 저장 완료"}

# 4. 알레르기 스캔
@router.post("/{account_id}/allergies/scan")
async def scan_allergy_test(
    account_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    gemini_service = get_gemini_service()
    
    image_bytes = await file.read()
    allergens = gemini_service.parse_allergy_test(image_bytes)
    
    # 분석 실패 시 빈 리스트
    if allergens is None:
        allergens = []
        # raise HTTPException(status_code=400, detail="알레르기 검사지 분석 실패")
    
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
    
    # [Async] 추천 데이터 갱신
    background_tasks.add_task(update_user_recommendation, user.id)

    return {"message": f"{count}개의 알레르기 정보가 추가되었습니다.", "allergens": allergens}

# 5. 알레르기 수동 등록
@router.post("/{account_id}/allergies")
async def add_allergy_manual(
    account_id: str,
    data: UserAllergyCreate,
    background_tasks: BackgroundTasks,
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
        
    # [Async] 추천 데이터 갱신
    background_tasks.add_task(update_user_recommendation, user.id)
        
    return {"message": "알레르기 추가 완료"}

# 6. 건강 리포트 생성 (건강 조언)
@router.get("/{account_id}/advice")
def get_health_advice(
    account_id: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_account_id(db, account_id)
    gemini_service = get_gemini_service()
    
    # 건강 정보 조회
    health_record = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    health_data = {}
    if health_record:
        # 주요 건강 지표만 추출
        for col in ["height", "weight", "bmi", "fasting_blood_sugar", "total_cholesterol", 
                    "ldl_cholesterol", "triglyceride", "bp_high", "bp_low"]:
            val = getattr(health_record, col, None)
            if val is not None:
                health_data[col] = val
                
    # 알레르기 정보 조회
    allergy_records = db.query(UserAllergy).filter(UserAllergy.user_id == user.id).all()
    allergens = [a.allergen_name for a in allergy_records]
    
    # Gemini를 이용해 조언 생성
    advice = gemini_service.generate_health_advice(health_data, allergens)
    
    return advice
