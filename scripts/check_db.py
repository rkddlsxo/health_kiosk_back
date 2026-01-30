import sys
import os
import json

# 현재 디렉토리의 부모를 sys.path에 추가 (app 모듈 사용)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app import models
from sqlalchemy import text

def check_db():
    db = SessionLocal()
    
    print("="*50)
    print(" [DB 데이터 확인] ")
    print("="*50)
    
    # 1. 사용자 확인
    users = db.query(models.User).all()
    print(f"\n[Users] 총 {len(users)}명")
    for u in users:
        print(f"ID: {u.id}, Account: {u.account_id}, Name: {u.name}")
        
    # 2. 건강 정보 확인
    print(f"\n[Health Data]")
    healths = db.query(models.UserHealth).all()
    for h in healths:
        print(f"User ID: {h.user_id}")
        print(f"  - 신체계측: 키 {h.height}, 몸무게 {h.weight}, 허리 {h.waist}, BMI {h.bmi}")
        print(f"  - 시력/청력: 좌 {h.vision_l}/{h.hearing_l}, 우 {h.vision_r}/{h.hearing_r}")
        print(f"  - 혈압: {h.bp_high}/{h.bp_low}")
        print(f"  - 요검사(단백): {h.urine_protein}")
        print(f"  - 혈액(일반): 빈혈 {h.hemoglobin}, 혈당 {h.fasting_blood_sugar}")
        print(f"  - 혈액(지질): 총콜 {h.total_cholesterol}, HDL {h.hdl_cholesterol}, LDL {h.ldl_cholesterol}, 중성지방 {h.triglyceride}")
        print(f"  - 혈액(신장): 크레아티닌 {h.creatinine}")
        print(f"  - 간기능: AST {h.ast}, ALT {h.alt}, r-GTP {h.gamma_gtp}")
        print(f"  - 기타: B형간염 {h.hepatitis_b_antigen}/{h.hepatitis_b_antibody}, 흉부 {h.chest_xray}")
        
    # 3. 알레르기 정보 확인
    print(f"\n[Allergies]")
    allergies = db.query(models.UserAllergy).all()
    for a in allergies:
        print(f"User ID: {a.user_id} | 알레르기: {a.allergen_name} ({a.reaction or '반응없음'})")
        
    # 4. 얼굴 데이터 확인 (임베딩 길이만 체크)
    print(f"\n[Face Data]")
    faces = db.query(models.UserFace).all()
    for f in faces:
        emb_len = len(f.embedding) if f.embedding else 0
        is_json = False
        try:
            json.loads(f.embedding)
            is_json = True
        except:
            pass
        print(f"User ID: {f.user_id} | Embedding Length: {emb_len} chars | Valid JSON: {is_json}")

    # 5. 메뉴 데이터 확인 (전체)
    menus = db.query(models.Menu).all()
    print(f"\n[Menus] 총 {len(menus)}개")
    for m in menus:
        print(f"ID: {m.id} | {m.name} ({m.category}) - {m.price}원 | 알레르기: {m.allergens}")

    db.close()

if __name__ == "__main__":
    check_db()
