from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserFace(Base):
    """사용자 얼굴 임베딩 모델"""
    __tablename__ = "user_faces"
    
    user_face_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 얼굴 특징 벡터 (512 float array를 JSON으로 저장)
    embedding = Column(JSON, nullable=False)
    
    # 사용 모델명
    embedding_model = Column(String(50), default="arcface-r100", nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="face")
    
    def __repr__(self):
        return f"<UserFace(user_id={self.user_id}, model={self.embedding_model})>"
