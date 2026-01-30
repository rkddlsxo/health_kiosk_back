from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import User
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "mysql+pymysql://root:1234@localhost:3306/health_kiosk")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print(f"Checking User ID 1...")
    user = db.query(User).filter(User.id == 1).first()
    
    if not user:
        print("❌ User 1 not found!")
    else:
        print(f"User Name: {user.name}")
        print("Checking recommendation_cache column...")
        
        # 컬럼 존재 여부 확인 (SQLAlchemy 모델 통해 접근)
        if user.recommendation_cache:
            print("✅ Data found in recommendation_cache!")
            print(f"Length: {len(user.recommendation_cache)} chars")
            try:
                data = json.loads(user.recommendation_cache)
                print("✅ JSON Parsing Success!")
                print(f"Keys: {list(data.keys())}")
                print(f"Recommended Menus: {len(data.get('recommended_menus', []))}")
            except Exception as e:
                 print(f"❌ JSON Parsing Failed: {e}")
                 print(f"Raw Data: {user.recommendation_cache[:100]}...")
        else:
            print("❌ recommendation_cache is EMPTY or NULL!")
            
except Exception as e:
    print(f"❌ Database Error: {e}")
finally:
    db.close()
