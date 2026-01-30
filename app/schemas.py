from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# 1. 로그인 할 때 받는 데이터 
class UserLogin(BaseModel):
    account_id: str
    password: str

# 2. 회원가입 할 때 받는 데이터
class UserCreate(BaseModel):
    account_id: str
    password: str
    name: str

# 3. 유저 정보 응답 (비밀번호 제외)
class UserResponse(BaseModel):
    account_id: str
    name: str
    class Config:
        from_attributes = True

# 4. 알레르기 등록 데이터
class AllergyCreate(BaseModel):
    allergen_name: str
    reaction: Optional[str] = None
    severity: Optional[str] = None

# 5. 건강검진 결과 등록 데이터 (모든 항목 Optional 처리)
class HealthRecordCreate(BaseModel):
    checkup_date: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    waist: Optional[float] = None
    bmi: Optional[float] = None
    
    # 시력/청력
    vision_l: Optional[float] = None
    vision_r: Optional[float] = None
    hearing_l: Optional[str] = None
    hearing_r: Optional[str] = None
    
    # 혈압/소변
    bp_high: Optional[int] = None
    bp_low: Optional[int] = None
    urine_protein: Optional[str] = None
    
    # 혈액검사
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
    
    # 기타
    hepatitis_b_antigen: Optional[str] = None
    hepatitis_b_antibody: Optional[str] = None
    chest_xray: Optional[str] = None