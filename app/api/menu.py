"""
메뉴 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.menu import Menu, MenuOption

router = APIRouter()


@router.get("/")
def get_all_menus(db: Session = Depends(get_db)):
    """
    전체 메뉴 조회
    """
    menus = db.query(Menu).all()
    return menus


@router.get("/{menu_id}")
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """
    특정 메뉴 상세 조회
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다")
    
    return menu


@router.get("/{menu_id}/options")
def get_menu_options(menu_id: int, db: Session = Depends(get_db)):
    """
    특정 메뉴의 옵션 조회
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다")
    
    options = db.query(MenuOption).filter(MenuOption.menu_id == menu_id).all()
    return options
