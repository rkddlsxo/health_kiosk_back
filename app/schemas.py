from pydantic import BaseModel

# 회원가입 때 받을 데이터
class UserCreate(BaseModel):
    account_id: str
    password: str
    name: str

# 응답으로 줄 데이터
class UserResponse(BaseModel):
    account_id: str
    name: str

    class Config:
        from_attributes = True