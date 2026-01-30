import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Menu, MenuOption

def init_db():
    # 테이블 다시 생성 (스키마 변경 반영)
    print("테이블 재생성 중...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    print("메뉴 데이터 추가 중...")
    menus = [
        Menu(name='아이스 아메리카노', price=2000, category='coffee', image_url='ice_americano.jpg', allergens=None, calories=10, carbs=2, protein=0.5, fat=0, sugar=0, sodium=5),
        Menu(name='따뜻한 아메리카노', price=2000, category='coffee', image_url='hot_americano.jpg', allergens=None, calories=10, carbs=2, protein=0.5, fat=0, sugar=0, sodium=5),
        Menu(name='카페 라떼', price=3500, category='coffee', image_url='latte.jpg', allergens='우유', calories=180, carbs=10, protein=8, fat=7, sugar=9, sodium=80),
        Menu(name='바닐라 라떼', price=4000, category='coffee', image_url='vanilla_latte.jpg', allergens='우유', calories=240, carbs=30, protein=8, fat=7, sugar=28, sodium=85),
        Menu(name='카라멜 마키아또', price=4500, category='coffee', image_url='caramel_macchiato.jpg', allergens='우유,대두', calories=280, carbs=40, protein=8, fat=8, sugar=35, sodium=90),
        Menu(name='카페 모카', price=4500, category='coffee', image_url='mocha.jpg', allergens='우유,대두', calories=330, carbs=45, protein=9, fat=11, sugar=38, sodium=95),
        Menu(name='연유 라떼', price=4800, category='coffee', image_url='condensed_latte.jpg', allergens='우유', calories=350, carbs=50, protein=9, fat=10, sugar=42, sodium=100),
        Menu(name='콜드브루', price=3000, category='coffee', image_url='coldbrew.jpg', allergens=None, calories=15, carbs=3, protein=0, fat=0, sugar=0, sodium=5),
        Menu(name='콜드브루 라떼', price=4000, category='coffee', image_url='coldbrew_latte.jpg', allergens='우유', calories=160, carbs=8, protein=6, fat=6, sugar=6, sodium=70),
        Menu(name='에스프레소', price=2000, category='coffee', image_url='espresso.jpg', allergens=None, calories=5, carbs=1, protein=0, fat=0, sugar=0, sodium=0),
        Menu(name='초코 라떼', price=4000, category='beverage', image_url='choco_latte.jpg', allergens='우유,대두', calories=380, carbs=55, protein=8, fat=12, sugar=45, sodium=120),
        Menu(name='녹차 라떼', price=4200, category='beverage', image_url='greentea_latte.jpg', allergens='우유', calories=280, carbs=35, protein=7, fat=8, sugar=30, sodium=90),
        Menu(name='고구마 라떼', price=4300, category='beverage', image_url='sweetpotato_latte.jpg', allergens='우유', calories=300, carbs=45, protein=6, fat=7, sugar=32, sodium=110),
        Menu(name='토피넛 라떼', price=4500, category='beverage', image_url='toffeenut_latte.jpg', allergens='우유,견과류', calories=320, carbs=38, protein=7, fat=10, sugar=28, sodium=105),
        Menu(name='민트 초코 라떼', price=4500, category='beverage', image_url='mintchoco.jpg', allergens='우유,대두', calories=360, carbs=50, protein=8, fat=11, sugar=42, sodium=115),
        Menu(name='캐모마일 티', price=3000, category='tea', image_url='chamomile.jpg', allergens=None, calories=0, carbs=0, protein=0, fat=0, sugar=0, sodium=0),
        Menu(name='페퍼민트 티', price=3000, category='tea', image_url='peppermint.jpg', allergens=None, calories=0, carbs=0, protein=0, fat=0, sugar=0, sodium=0),
        Menu(name='유자차', price=3500, category='tea', image_url='citron_tea.jpg', allergens=None, calories=150, carbs=38, protein=0, fat=0, sugar=35, sodium=5),
        Menu(name='얼그레이 티', price=3000, category='tea', image_url='earlgrey.jpg', allergens=None, calories=0, carbs=0, protein=0, fat=0, sugar=0, sodium=0),
        Menu(name='아이스티 복숭아', price=3000, category='tea', image_url='iced_tea.jpg', allergens='복숭아', calories=180, carbs=45, protein=0, fat=0, sugar=42, sodium=15),
        Menu(name='플레인 요거트 스무디', price=4800, category='smoothie', image_url='yogurt_smoothie.jpg', allergens='우유', calories=350, carbs=50, protein=8, fat=9, sugar=45, sodium=130),
        Menu(name='딸기 요거트 스무디', price=5200, category='smoothie', image_url='berry_smoothie.jpg', allergens='우유', calories=380, carbs=60, protein=7, fat=8, sugar=55, sodium=125),
        Menu(name='망고 스무디', price=5000, category='smoothie', image_url='mango_smoothie.jpg', allergens=None, calories=320, carbs=70, protein=1, fat=0, sugar=65, sodium=10),
        Menu(name='레몬 에이드', price=4000, category='ade', image_url='lemonade.jpg', allergens=None, calories=180, carbs=45, protein=0, fat=0, sugar=42, sodium=20),
        Menu(name='자몽 에이드', price=4200, category='ade', image_url='grapefruit_ade.jpg', allergens=None, calories=190, carbs=48, protein=0, fat=0, sugar=45, sodium=20),
        Menu(name='청포도 에이드', price=4200, category='ade', image_url='grape_ade.jpg', allergens=None, calories=200, carbs=50, protein=0, fat=0, sugar=48, sodium=25),
        Menu(name='토마토 주스', price=4500, category='juice', image_url='tomato_juice.jpg', allergens='토마토', calories=90, carbs=20, protein=2, fat=0, sugar=15, sodium=30),
        Menu(name='케일 사과 주스', price=5500, category='juice', image_url='kale_juice.jpg', allergens=None, calories=110, carbs=25, protein=2, fat=0, sugar=18, sodium=10),
        Menu(name='제로 콜라', price=2000, category='soda', image_url='zero_coke.jpg', allergens=None, calories=0, carbs=0, protein=0, fat=0, sugar=0, sodium=10),
        Menu(name='프로틴 쉐이크 (초코)', price=4500, category='shake', image_url='protein_shake.jpg', allergens='우유,대두', calories=210, carbs=10, protein=25, fat=3, sugar=2, sodium=160)
    ]
    
    db.add_all(menus)
    db.flush() # ID 생성을 위해 flush
    
    print("메뉴 옵션 추가 중...")
    options = []
    for menu in menus:
        # 공통 옵션
        options.append(MenuOption(menu_id=menu.id, option_name='기본', price_change=0))
        
        # 카테고리별 옵션
        if menu.category == 'coffee':
            options.append(MenuOption(menu_id=menu.id, option_name='샷 추가', price_change=500))
            if 'ice' not in menu.name and 'hot' not in menu.name:
                options.append(MenuOption(menu_id=menu.id, option_name='ICE', price_change=0))
                options.append(MenuOption(menu_id=menu.id, option_name='HOT', price_change=0))
        elif 'latte' in menu.name:
            options.append(MenuOption(menu_id=menu.id, option_name='우유 → 두유 변경', price_change=0))
            options.append(MenuOption(menu_id=menu.id, option_name='저지방 우유 변경', price_change=0))
            
    db.add_all(options)
    db.commit()
    db.close()
    print(f"메뉴 {len(menus)}개 및 옵션 데이터 초기화 완료!")

if __name__ == "__main__":
    init_db()
