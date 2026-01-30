from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Menu(Base):
    """메뉴 모델"""
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # 커피, 음료, 디저트 등
    description = Column(String(500), nullable=True)
    price = Column(Integer, nullable=False)
    
    # 기본 재료 (JSON 배열)
    # 예: ["milk", "espresso", "vanilla_syrup"]
    base_ingredients = Column(JSON, default=list, nullable=False)
    
    # 알러지 유발 성분 (JSON 배열)
    # 예: ["milk", "nuts"]
    allergens = Column(JSON, default=list, nullable=False)
    
    # 기본 영양 정보 (JSON 객체)
    # 예: {"sugar": 20, "fat": 5, "calories": 150, "caffeine": 75}
    nutrition = Column(JSON, default=dict, nullable=False)
    
    # 사용 가능한 옵션 타입 (JSON 배열)
    # 예: ["milk_type", "syrup", "size", "ice", "shot"]
    available_option_types = Column(JSON, default=list, nullable=False)
    
    # 관계
    options = relationship("MenuOption", back_populates="menu", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Menu(id={self.id}, name={self.name}, category={self.category})>"


class MenuOption(Base):
    """메뉴 옵션 모델"""
    __tablename__ = "menu_options"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    
    # 옵션 타입 (milk_type, syrup, size, shot, ice 등)
    option_type = Column(String(50), nullable=False)
    
    # 옵션 값 (regular, low-fat, oat, soy 등)
    option_value = Column(String(50), nullable=False)
    
    # 추가 가격
    additional_price = Column(Integer, default=0, nullable=False)
    
    # 영양 변화량 (JSON 객체)
    # 예: {"sugar": +5, "fat": -3, "calories": +20}
    nutrition_modifier = Column(JSON, default=dict, nullable=False)
    
    # 관계
    menu = relationship("Menu", back_populates="options")
    
    def __repr__(self):
        return f"<MenuOption(menu_id={self.menu_id}, type={self.option_type}, value={self.option_value})>"
