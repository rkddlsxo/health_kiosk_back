from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserHealthCreate(BaseModel):
    """건강 정보 생성 스키마"""
    checkup_date: Optional[date] = None
    
    # 계측 검사
    height: Optional[float] = None
    weight: Optional[float] = None
    waist: Optional[float] = None
    bmi: Optional[float] = None
    vision_l: Optional[float] = None
    vision_r: Optional[float] = None
    hearing_l: Optional[str] = None
    hearing_r: Optional[str] = None
    bp_high: Optional[int] = None
    bp_low: Optional[int] = None
    
    # 요검사
    urine_protein: Optional[str] = None
    
    # 혈액 검사
    hemoglobin: Optional[float] = None
    fasting_blood_sugar: Optional[int] = None
    total_cholesterol: Optional[int] = None
    hdl_cholesterol: Optional[int] = None
    triglyceride: Optional[int] = None
    ldl_cholesterol: Optional[int] = None
    creatinine: Optional[float] = None
    ast: Optional[int] = None
    alt: Optional[int] = None
    gamma_gtp: Optional[int] = None
    
    # 기타 검사
    hepatitis_b_antigen: Optional[str] = None
    hepatitis_b_antibody: Optional[str] = None
    chest_xray: Optional[str] = None


class UserHealthResponse(UserHealthCreate):
    """건강 정보 응답 스키마"""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class UserAllergyCreate(BaseModel):
    """알러지 정보 생성 스키마"""
    allergen_name: str
    reaction: Optional[str] = None
    severity: Optional[str] = None  # High, Medium, Low


class UserAllergyResponse(UserAllergyCreate):
    """알러지 정보 응답 스키마"""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
