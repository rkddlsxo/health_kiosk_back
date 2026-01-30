from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)  # Hashed
    name = Column(String(50), nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    health = relationship("UserHealth", back_populates="user", uselist=False)
    allergies = relationship("UserAllergy", back_populates="user")
    face = relationship("UserFace", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, account_id={self.account_id}, name={self.name})>"
