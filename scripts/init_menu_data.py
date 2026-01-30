import sys
import os

# 현재 디렉토리(scripts)의 부모(health_kiosk_back)를 sys.path에 추가 (app 모듈 찾기 위함)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def init_menu_data():
    db = SessionLocal()
    
    # 기존 메뉴 삭제 (옵션)
    # db.query(models.Menu).delete()
    # db.commit()
    
    # 메뉴 데이터 확인
    existing_count = db.query(models.Menu).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 메뉴가 존재합니다. 초기화를 건너뜁니다.")
        # db.close()
        # return

    # 샘플 메뉴 리스트
    sample_menus = [
        {
            "name": "아메리카노",
            "price": 4500,
            "category": "COFFEE",
            "image_url": "https://img.freepik.com/free-photo/fresh-coffee-steams-wooden-table-close-up-generative-ai_188544-8923.jpg",
            "allergens": "",
            "calories": 10,
            "carbs": 1.0,
            "protein": 0.5,
            "fat": 0.0,
            "sugar": 0.0,
            "sodium": 5.0
        },
        {
            "name": "카페라떼",
            "price": 5000,
            "category": "COFFEE", 
            "image_url": "https://img.freepik.com/free-photo/cup-coffee-with-heart-drawn-foam_1286-70.jpg",
            "allergens": "우유",
            "calories": 180,
            "carbs": 12.0,
            "protein": 6.0,
            "fat": 5.0,
            "sugar": 10.0,
            "sodium": 80.0
        },
        {
            "name": "카푸치노",
            "price": 5000,
            "category": "COFFEE",
            "image_url": "https://img.freepik.com/free-photo/close-up-coffee-cup-table_23-2148178225.jpg",
            "allergens": "우유",
            "calories": 150,
            "carbs": 10.0,
            "protein": 5.0,
            "fat": 5.0,
            "sugar": 9.0,
            "sodium": 70.0
        },
        {
            "name": "바닐라 라떼",
            "price": 5500,
            "category": "COFFEE",
            "image_url": "https://img.freepik.com/free-photo/coffee-cup-latte-art-placed-wooden-floor_1150-12822.jpg",
            "allergens": "우유",
            "calories": 250,
            "carbs": 30.0,
            "protein": 6.0,
            "fat": 6.0,
            "sugar": 25.0,
            "sodium": 90.0
        },
        {
            "name": "딸기 스무디",
            "price": 6000,
            "category": "BEVERAGE",
            "image_url": "https://img.freepik.com/free-photo/strawberry-smoothie-glass-jar_140725-3738.jpg",
            "allergens": "우유",
            "calories": 350,
            "carbs": 60.0,
            "protein": 4.0,
            "fat": 2.0,
            "sugar": 50.0,
            "sodium": 40.0
        },
        {
            "name": "레몬 에이드",
            "price": 5500,
            "category": "BEVERAGE",
            "image_url": "https://img.freepik.com/free-photo/lemonade-glass-with-lemon-slices-ice-cubes_1150-41882.jpg",
            "allergens": "",
            "calories": 200,
            "carbs": 45.0,
            "protein": 0.0,
            "fat": 0.0,
            "sugar": 40.0,
            "sodium": 10.0
        },
        {
            "name": "초코 케이크",
            "price": 6500,
            "category": "DESSERT",
            "image_url": "https://img.freepik.com/free-photo/chocolate-cake-with-chocolate-sprinkles_144627-8998.jpg",
            "allergens": "우유,밀가루,계란,대두",
            "calories": 450,
            "carbs": 55.0,
            "protein": 5.0,
            "fat": 25.0,
            "sugar": 35.0,
            "sodium": 200.0
        },
        {
            "name": "치즈 케이크",
            "price": 6500,
            "category": "DESSERT",
            "image_url": "https://img.freepik.com/free-photo/cheesecake-with-berries_144627-18305.jpg",
            "allergens": "우유,밀가루,계란",
            "calories": 400,
            "carbs": 40.0,
            "protein": 6.0,
            "fat": 22.0,
            "sugar": 25.0,
            "sodium": 250.0
        },
        {
            "name": "샌드위치",
            "price": 7000,
            "category": "FOOD",
            "image_url": "https://img.freepik.com/free-photo/sandwich-with-ham-cheese-vegetables_144627-14736.jpg",
            "allergens": "밀가루,계란,우유,토마토",
            "calories": 350,
            "carbs": 35.0,
            "protein": 15.0,
            "fat": 12.0,
            "sugar": 5.0,
            "sodium": 600.0
        },
        {
            "name": "땅콩 쿠키",
            "price": 3000,
            "category": "DESSERT",
            "image_url": "https://img.freepik.com/free-photo/oatmeal-cookies_144627-16723.jpg",
            "allergens": "밀가루,계란,땅콩,우유",
            "calories": 280,
            "carbs": 30.0,
            "protein": 4.0,
            "fat": 15.0,
            "sugar": 15.0,
            "sodium": 120.0
        }
    ]

    print("메뉴 데이터 삽입 중...")
    for menu_data in sample_menus:
        # 이름 중복 확인
        exists = db.query(models.Menu).filter(models.Menu.name == menu_data["name"]).first()
        if not exists:
            new_menu = models.Menu(**menu_data)
            db.add(new_menu)
            print(f"추가됨: {menu_data['name']}")
        else:
            print(f"이미 존재함: {menu_data['name']}")
    
    db.commit()
    print("메뉴 데이터 초기화 완료!")
    db.close()

if __name__ == "__main__":
    init_menu_data()
