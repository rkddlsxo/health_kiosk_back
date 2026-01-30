"""
MySQL 연결 및 서버 검증 스크립트
"""
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("1. MySQL 연결 테스트...")
try:
    from app.database import engine, SessionLocal
    
    # 연결 테스트
    connection = engine.connect()
    print("✅ MySQL 연결 성공!")
    connection.close()
    
    # 데이터베이스 확인
    with SessionLocal() as session:
        result = session.execute("SELECT DATABASE()")
        db_name = result.scalar()
        print(f"✅ 현재 데이터베이스: {db_name}")
        
except Exception as e:
    print(f"❌ MySQL 연결 실패: {e}")
    print("\n해결 방법:")
    print("1. MySQL 서버가 실행 중인지 확인")
    print("2. 비밀번호가 맞는지 확인 (현재: root:1234)")
    print("3. kiosk 데이터베이스 생성:")
    print("   mysql -u root -p1234 -e 'CREATE DATABASE IF NOT EXISTS kiosk;'")
    sys.exit(1)

print("\n2. 테이블 생성...")
try:
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료!")
    
    # 생성된 테이블 확인
    with SessionLocal() as session:
        result = session.execute("SHOW TABLES")
        tables = [row[0] for row in result]
        print(f"✅ 생성된 테이블: {tables}")
        
except Exception as e:
    print(f"❌ 테이블 생성 실패: {e}")
    sys.exit(1)

print("\n3. 모델 import 테스트...")
try:
    from app import models, schemas
    print("✅ 모델 import 성공!")
except Exception as e:
    print(f"❌ 모델 import 실패: {e}")
    sys.exit(1)

print("\n✅ 모든 검증 완료! 서버를 실행할 수 있습니다.")
print("\n서버 실행 명령:")
print("  uvicorn app.main:app --reload")
