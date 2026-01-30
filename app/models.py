from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)      # 내부 관리용 고유 번호
    account_id = Column(String(50), unique=True, index=True) # 사용자가 로그인할 때 쓰는 아이디
    password = Column(String(100))                          # 비밀번호
    name = Column(String(50))                               # 이름