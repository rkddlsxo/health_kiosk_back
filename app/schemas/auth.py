from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    """사용자 생성 스키마"""
    account_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=50)


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    id: int
    account_id: str
    name: str
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    account_id: str
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    success: bool
    message: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
