"""
건강 정보 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserHealth, UserAllergy
from app.schemas.health import (
    UserHealthCreate,
    UserHealthResponse,
    UserAllergyCreate,
    UserAllergyResponse
)
from app.services.gemini_service import get_gemini_service
from typing import List

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/users/{user_id}/health-report", response_model=UserHealthResponse)
async def upload_health_report(
    user_id: int,
    health_report: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    건강검진표 이미지 업로드 및 자동 파싱
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # Gemini로 이미지 파싱
    gemini_service = get_gemini_service()
    image_bytes = await health_report.read()
    parsed_data = gemini_service.parse_health_report(image_bytes)
    
    if not parsed_data:
        raise HTTPException(status_code=400, detail="건강검진표 파싱에 실패했습니다")
    
    # 기존 건강 정보 확인
    existing_health = db.query(UserHealth).filter(UserHealth.user_id == user_id).first()
    
    if existing_health:
        # 업데이트
        for key, value in parsed_data.items():
            if hasattr(existing_health, key) and value is not None:
                setattr(existing_health, key, value)
        db.commit()
        db.refresh(existing_health)
        return existing_health
    else:
        # 새로 생성
        new_health = UserHealth(user_id=user_id, **parsed_data)
        db.add(new_health)
        db.commit()
        db.refresh(new_health)
        return new_health


@router.post("/users/{user_id}/health-profile", response_model=UserHealthResponse)
async def create_or_update_health_profile(
    user_id: int,
    health_data: UserHealthCreate,
    db: Session = Depends(get_db)
):
    """
    건강 프로필 직접 입력/수정
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    existing_health = db.query(UserHealth).filter(UserHealth.user_id == user_id).first()
    
    if existing_health:
        # 업데이트
        for key, value in health_data.dict(exclude_unset=True).items():
            if hasattr(existing_health, key) and value is not None:
                setattr(existing_health, key, value)
        db.commit()
        db.refresh(existing_health)
        return existing_health
    else:
        # 새로 생성
        new_health = UserHealth(user_id=user_id, **health_data.dict(exclude_unset=True))
        db.add(new_health)
        db.commit()
        db.refresh(new_health)
        return new_health


@router.get("/users/{user_id}/health-profile", response_model=UserHealthResponse)
async def get_health_profile(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 건강 프로필 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    health = db.query(UserHealth).filter(UserHealth.user_id == user_id).first()
    
    if not health:
        raise HTTPException(status_code=404, detail="건강 프로필이 없습니다")
    
    return health


@router.post("/users/{user_id}/allergy", response_model=List[UserAllergyResponse])
async def add_allergy(
    user_id: int,
    allergies: List[UserAllergyCreate],
    db: Session = Depends(get_db)
):
    """
    알러지 정보 추가 (기존 삭제 후 새로 추가)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 기존 알러지 정보 삭제
    db.query(UserAllergy).filter(UserAllergy.user_id == user_id).delete()
    
    # 새 알러지 정보 추가
    new_allergies = []
    for allergy_data in allergies:
        new_allergy = UserAllergy(user_id=user_id, **allergy_data.dict())
        db.add(new_allergy)
        new_allergies.append(new_allergy)
    
    db.commit()
    
    for allergy in new_allergies:
        db.refresh(allergy)
    
    return new_allergies


@router.get("/users/{user_id}/allergy", response_model=List[UserAllergyResponse])
async def get_allergies(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 알러지 정보 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    allergies = db.query(UserAllergy).filter(UserAllergy.user_id == user_id).all()
    
    return allergies
