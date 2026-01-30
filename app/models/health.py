from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserHealth(Base):
    """사용자 건강검진 상세 결과 모델"""
    __tablename__ = "user_health"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 건강검진 일자
    checkup_date = Column(Date, nullable=True)
    
    # ===== 계측 검사 =====
    height = Column(Float, nullable=True)  # 신장 (cm)
    weight = Column(Float, nullable=True)  # 체중 (kg)
    waist = Column(Float, nullable=True)  # 허리둘레 (cm)
    bmi = Column(Float, nullable=True)  # 체질량지수
    
    vision_l = Column(Float, nullable=True)  # 시력 (좌)
    vision_r = Column(Float, nullable=True)  # 시력 (우)
    
    hearing_l = Column(String(20), nullable=True)  # 청력 (좌) - 정상/비정상
    hearing_r = Column(String(20), nullable=True)  # 청력 (우)
    
    bp_high = Column(Integer, nullable=True)  # 수축기 혈압 (최고) mmHg
    bp_low = Column(Integer, nullable=True)  # 이완기 혈압 (최저) mmHg
    
    # ===== 요검사 =====
    urine_protein = Column(String(20), nullable=True)  # 요단백 - 음성/양성
    
    # ===== 혈액 검사 =====
    hemoglobin = Column(Float, nullable=True)  # 혈색소 (빈혈) g/dL
    fasting_blood_sugar = Column(Integer, nullable=True)  # 식전혈당 (공복) mg/dL
    
    total_cholesterol = Column(Integer, nullable=True)  # 총콜레스테롤 mg/dL
    hdl_cholesterol = Column(Integer, nullable=True)  # HDL 콜레스테롤 mg/dL
    triglyceride = Column(Integer, nullable=True)  # 중성지방 mg/dL
    ldl_cholesterol = Column(Integer, nullable=True)  # LDL 콜레스테롤 mg/dL
    
    creatinine = Column(Float, nullable=True)  # 혈청크레아티닌 (신장) mg/dL
    
    ast = Column(Integer, nullable=True)  # AST (SGOT) U/L
    alt = Column(Integer, nullable=True)  # ALT (SGPT) U/L
    gamma_gtp = Column(Integer, nullable=True)  # 감마지티피 (r-GTP) U/L
    
    # ===== 기타 검사 =====
    hepatitis_b_antigen = Column(String(20), nullable=True)  # B형간염 항원 - 음성/양성
    hepatitis_b_antibody = Column(String(20), nullable=True)  # B형간염 항체 - 음성/양성
    chest_xray = Column(String(50), nullable=True)  # 흉부방사선 검사 - 정상/비활동성 등
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="health")
    
    def __repr__(self):
        return f"<UserHealth(user_id={self.user_id}, checkup_date={self.checkup_date})>"


class UserAllergy(Base):
    """사용자 알레르기 정보 모델"""
    __tablename__ = "user_allergies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 알레르기 유발 물질
    allergen_name = Column(String(100), nullable=False)
    
    # 주요 반응
    reaction = Column(String(200), nullable=True)
    
    # 심각도
    severity = Column(String(20), nullable=True)  # High, Medium, Low
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="allergies")
    
    def __repr__(self):
        return f"<UserAllergy(user_id={self.user_id}, allergen={self.allergen_name}, severity={self.severity})>"
