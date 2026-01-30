"""
데이터베이스 테이블 초기화 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import User, UserFace, UserHealth, UserAllergy, Menu, MenuOption

print("데이터베이스 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ 데이터베이스 테이블 생성 완료!")
print("\n생성된 테이블:")
for table in Base.metadata.sorted_tables:
    print(f"  - {table.name}")
