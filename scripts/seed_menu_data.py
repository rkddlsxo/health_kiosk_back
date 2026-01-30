"""
메뉴 및 옵션 시드 데이터 생성 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.menu import Menu, MenuOption


def create_menu_data():
    """카페 메뉴 데이터 생성"""
    db = SessionLocal()
    
    try:
        # 기존 데이터 삭제
        db.query(MenuOption).delete()
        db.query(Menu).delete()
        db.commit()
        
        # 메뉴 데이터
        menus_data = [
            # 커피
            {
                "name": "아메리카노",
                "category": "커피",
                "description": "깔끔한 에스프레소",
                "price": 3000,
                "base_ingredients": ["espresso", "water"],
                "allergens": [],
                "nutrition": {"sugar": 0, "fat": 0, "calories": 10, "caffeine": 75},
                "options": ["size", "shot", "ice"]
            },
            {
                "name": "카페라떼",
                "category": "커피",
                "description": "부드러운 우유와 에스프레소",
                "price": 3500,
                "base_ingredients": ["espresso", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 10, "fat": 5, "calories": 150, "caffeine": 75},
                "options": ["milk_type", "size", "shot", "ice"]
            },
            {
                "name": "카푸치노",
                "category": "커피",
                "description": "풍부한 거품의 커피",
                "price": 3500,
                "base_ingredients": ["espresso", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 8, "fat": 4, "calories": 120, "caffeine": 75},
                "options": ["milk_type", "size", "shot"]
            },
            {
                "name": "바닐라라떼",
                "category": "커피",
                "description": "달콤한 바닐라 향의 라떼",
                "price": 4000,
                "base_ingredients": ["espresso", "milk", "vanilla_syrup"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 25, "fat": 5, "calories": 220, "caffeine": 75},
                "options": ["milk_type", "size", "shot", "ice", "syrup"]
            },
            {
                "name": "카라멜마끼아또",
                "category": "커피",
                "description": "달콤한 카라멜 소스",
                "price": 4500,
                "base_ingredients": ["espresso", "milk", "caramel_syrup"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 30, "fat": 6, "calories": 250, "caffeine": 75},
                "options": ["milk_type", "size", "shot", "ice"]
            },
            {
                "name": "카페모카",
                "category": "커피",
                "description": "초콜릿과 커피의 조화",
                "price": 4500,
                "base_ingredients": ["espresso", "milk", "chocolate_syrup", "whipped_cream"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 35, "fat": 10, "calories": 320, "caffeine": 85},
                "options": ["milk_type", "size", "shot", "ice"]
            },
            
            # 음료
            {
                "name": "녹차라떼",
                "category": "음료",
                "description": "진한 녹차향",
                "price": 4000,
                "base_ingredients": ["green_tea", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 20, "fat": 5, "calories": 180, "caffeine": 30},
                "options": ["milk_type", "size", "ice"]
            },
            {
                "name": "초코라떼",
                "category": "음료",
                "description": "달콤한 초콜릿",
                "price": 4000,
                "base_ingredients": ["chocolate", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 30, "fat": 8, "calories": 280, "caffeine": 20},
                "options": ["milk_type", "size", "ice"]
            },
            {
                "name": "딸기스무디",
                "category": "음료",
                "description": "상큼한 딸기",
                "price": 4500,
                "base_ingredients": ["strawberry", "milk", "ice"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 35, "fat": 3, "calories": 220, "caffeine": 0},
                "options": ["size"]
            },
            {
                "name": "망고스무디",
                "category": "음료",
                "description": "열대 망고",
                "price": 4500,
                "base_ingredients": ["mango", "milk", "ice"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 40, "fat": 3, "calories": 250, "caffeine": 0},
                "options": ["size"]
            },
            {
                "name": "레모네이드",
                "category": "음료",
                "description": "상큼한 레몬",
                "price": 3500,
                "base_ingredients": ["lemon", "sugar", "water"],
                "allergens": [],
                "nutrition": {"sugar": 25, "fat": 0, "calories": 100, "caffeine": 0},
                "options": ["size", "ice"]
            },
            {
                "name": "자몽에이드",
                "category": "음료",
                "description": "새콤달콤 자몽",
                "price": 4000,
                "base_ingredients": ["grapefruit", "sugar", "sparkling_water"],
                "allergens": [],
                "nutrition": {"sugar": 20, "fat": 0, "calories": 90, "caffeine": 0},
                "options": ["size", "ice"]
            },
            
            # 디저트
            {
                "name": "초코칩쿠키",
                "category": "디저트",
                "description": "바삭한 초코칩 쿠키",
                "price": 2500,
                "base_ingredients": ["flour", "butter", "chocolate_chips", "egg"],
                "allergens": ["wheat", "milk", "egg"],
                "nutrition": {"sugar": 15, "fat": 12, "calories": 250, "caffeine": 5},
                "options": []
            },
            {
                "name": "치즈케이크",
                "category": "디저트",
                "description": "부드러운 치즈케이크",
                "price": 5000,
                "base_ingredients": ["cream_cheese", "egg", "sugar", "butter"],
                "allergens": ["milk", "egg", "wheat"],
                "nutrition": {"sugar": 25, "fat": 20, "calories": 350, "caffeine": 0},
                "options": []
            },
            {
                "name": "티라미수",
                "category": "디저트",
                "description": "이탈리아 디저트",
                "price": 5500,
                "base_ingredients": ["mascarpone", "coffee", "egg", "sugar"],
                "allergens": ["milk", "egg", "wheat"],
                "nutrition": {"sugar": 20, "fat": 18, "calories": 320, "caffeine": 40},
                "options": []
            },
            {
                "name": "크루아상",
                "category": "디저트",
                "description": "버터 향 가득",
                "price": 3000,
                "base_ingredients": ["flour", "butter"],
                "allergens": ["wheat", "milk"],
                "nutrition": {"sugar": 5, "fat": 15, "calories": 230, "caffeine": 0},
                "options": []
            },
            {
                "name": "마카롱",
                "category": "디저트",
                "description": "프랑스 전통 과자",
                "price": 2000,
                "base_ingredients": ["almond", "egg_white", "sugar"],
                "allergens": ["nuts", "egg"],
                "nutrition": {"sugar": 12, "fat": 5, "calories": 100, "caffeine": 0},
                "options": []
            },
        ]
        
        # 메뉴 생성
        created_menus = []
        for menu_data in menus_data:
            options = menu_data.pop("options")
            menu = Menu(**menu_data)
            menu.available_option_types = options
            db.add(menu)
            db.flush()  # ID 생성
            created_menus.append((menu, options))
        
        # 옵션 데이터 생성
        option_templates = {
            "milk_type": [
                {"value": "regular", "price": 0, "nutrition": {}},
                {"value": "low_fat", "price": 0, "nutrition": {"fat": -2, "calories": -20}},
                {"value": "skim", "price": 0, "nutrition": {"fat": -5, "calories": -50}},
                {"value": "oat", "price": 500, "nutrition": {"fat": -2}},
                {"value": "soy", "price": 500, "nutrition": {"fat": -3}},
            ],
            "size": [
                {"value": "small", "price": -500, "nutrition": {"sugar": -5, "fat": -2, "calories": -50}},
                {"value": "regular", "price": 0, "nutrition": {}},
                {"value": "large", "price": 500, "nutrition": {"sugar": 5, "fat": 2, "calories": 50}},
            ],
            "shot": [
                {"value": "normal", "price": 0, "nutrition": {}},
                {"value": "extra", "price": 500, "nutrition": {"caffeine": 75}},
                {"value": "decaf", "price": 500, "nutrition": {"caffeine": -70}},
            ],
            "ice": [
                {"value": "normal", "price": 0, "nutrition": {}},
                {"value": "less", "price": 0, "nutrition": {}},
                {"value": "none", "price": 0, "nutrition": {}},
            ],
            "syrup": [
                {"value": "none", "price": 0, "nutrition": {}},
                {"value": "vanilla", "price": 500, "nutrition": {"sugar": 15, "calories": 60}},
                {"value": "caramel", "price": 500, "nutrition": {"sugar": 15, "calories": 60}},
                {"value": "hazelnut", "price": 500, "nutrition": {"sugar": 12, "calories": 50}},
            ],
        }
        
        for menu, option_types in created_menus:
            for option_type in option_types:
                if option_type in option_templates:
                    for opt in option_templates[option_type]:
                        menu_option = MenuOption(
                            menu_id=menu.id,
                            option_type=option_type,
                            option_value=opt["value"],
                            additional_price=opt["price"],
                            nutrition_modifier=opt["nutrition"]
                        )
                        db.add(menu_option)
        
        db.commit()
        print(f"✅ 메뉴 {len(menus_data)}개 생성 완료!")
        
        # 생성된 메뉴 출력
        menus = db.query(Menu).all()
        for menu in menus:
            print(f"  - {menu.name} ({menu.category}): {menu.price}원")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("메뉴 시드 데이터 생성 시작...")
    create_menu_data()
