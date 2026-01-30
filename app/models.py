from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# 1. 사용자 기본 정보 (계정)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    name = Column(String(50))
    
    # 관계 설정 (1명의 유저는 여러 정보를 가질 수 있음)
    health_records = relationship("UserHealth", back_populates="owner")
    allergies = relationship("UserAllergy", back_populates="owner")
    face_data = relationship("UserFace", back_populates="owner")

# 2. 건강검진 상세 결과 (건강검진 결과표 항목 반영)
class UserHealth(Base):
    __tablename__ = "user_health"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # 유저와 연결
    checkup_date = Column(Date, nullable=True) # 검진일

    # --- 계측 검사 ---
    height = Column(Float, nullable=True)        # 신장 (cm)
    weight = Column(Float, nullable=True)        # 체중 (kg)
    waist = Column(Float, nullable=True)         # 허리둘레 (cm)
    bmi = Column(Float, nullable=True)           # 체질량지수
    vision_l = Column(Float, nullable=True)      # 시력(좌)
    vision_r = Column(Float, nullable=True)      # 시력(우)
    hearing_l = Column(String(20), nullable=True) # 청력(좌) - 정상/비정상
    hearing_r = Column(String(20), nullable=True) # 청력(우)
    bp_high = Column(Integer, nullable=True)     # 혈압(최고/수축기)
    bp_low = Column(Integer, nullable=True)      # 혈압(최저/이완기)

    # --- 요검사 ---
    urine_protein = Column(String(20), nullable=True) # 요단백 (음성/양성)

    # --- 혈액 검사 ---
    hemoglobin = Column(Float, nullable=True)    # 혈색소 (빈혈)
    fasting_blood_sugar = Column(Integer, nullable=True) # 식전혈당 (당뇨)
    total_cholesterol = Column(Integer, nullable=True)   # 총콜레스테롤
    hdl_cholesterol = Column(Integer, nullable=True)     # HDL
    triglyceride = Column(Integer, nullable=True)        # 중성지방
    ldl_cholesterol = Column(Integer, nullable=True)     # LDL
    creatinine = Column(Float, nullable=True)            # 혈청크레아티닌 (신장)
    ast = Column(Integer, nullable=True)                 # AST (간)
    alt = Column(Integer, nullable=True)                 # ALT (간)
    gamma_gtp = Column(Integer, nullable=True)           # r-GTP (간)
    
    # --- 간염 검사 ---
    hepatitis_b_antigen = Column(String(20), nullable=True) # B형간염항원
    hepatitis_b_antibody = Column(String(20), nullable=True) # B형간염항체

    # --- 영상 검사 ---
    chest_xray = Column(String(50), nullable=True) # 흉부방사선

    owner = relationship("User", back_populates="health_records")

# 3. 알레르기 정보 (별도 관리)
class UserAllergy(Base):
    __tablename__ = "user_allergies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    allergen_name = Column(String(100)) # 알레르기 유발 물질 (예: 땅콩, 페니실린)
    reaction = Column(String(200), nullable=True) # 증상 (예: 두드러기, 호흡곤란)
    severity = Column(String(20), nullable=True)  # 심각도 (경미/심각)

    owner = relationship("User", back_populates="allergies")

# 4. 얼굴 인식 데이터 (Vector 저장)
class UserFace(Base):
    __tablename__ = "user_faces"

    user_face_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 얼굴 특징 벡터 (보통 128~512개의 실수 배열이므로 긴 문자열이나 JSON으로 저장)
    embedding = Column(String(4000)) # JSON 문자열로 저장 권장
    embedding_model = Column(String(50), default="arcface-r100")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="face_data")