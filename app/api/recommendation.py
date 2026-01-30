"""
메뉴 추천 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserHealth, UserAllergy, Menu
from app.services.gemini_service import get_gemini_service

router = APIRouter(prefix="/api/recommend", tags=["recommendation"])


@router.get("/{user_id}")
async def get_menu_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 맞춤 메뉴 추천
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 건강 정보 가져오기
    health = db.query(UserHealth).filter(UserHealth.user_id == user_id).first()
    if not health:
        raise HTTPException(status_code=404, detail="건강 정보가 없습니다. 먼저 건강검진표를 등록해주세요.")
    
    # 알러지 정보 가져오기
    allergies = db.query(UserAllergy).filter(UserAllergy.user_id == user_id).all()
    allergen_list = [allergy.allergen_name for allergy in allergies]
    
    # 모든 메뉴 가져오기
    menus = db.query(Menu).all()
    
    # 메뉴를 딕셔너리로 변환
    menu_list = []
    for menu in menus:
        menu_dict = {
            "id": menu.id,
            "name": menu.name,
            "category": menu.category,
            "ingredients": menu.base_ingredients,
            "allergens": menu.allergens,
            "nutrition": {
                "sugar": menu.sugar_g,
                "fat": menu.fat_g,
                "calories": menu.calories,
                "caffeine": menu.caffeine_mg
            }
        }
        menu_list.append(menu_dict)
    
    # 건강 데이터를 딕셔너리로 변환 (null이 아닌 값만)
    health_dict = {}
    for key in [
        "fasting_blood_sugar", "total_cholesterol", "hdl_cholesterol", 
        "ldl_cholesterol", "triglyceride", "bp_high", "bp_low",
        "bmi", "waist", "hemoglobin", "ast", "alt", "gamma_gtp",
        "creatinine"
    ]:
        value = getattr(health, key, None)
        if value is not None:
            health_dict[key] = value
    
    # Gemini로 메뉴 추천 생성
    gemini_service = get_gemini_service()
    recommendations = gemini_service.generate_menu_recommendations(
        health_data=health_dict,
        allergens=allergen_list,
        menus=menu_list
    )
    
    # 메뉴 ID를 메뉴 정보로 변환
    result = {
        "user_name": user.name,
        "health_summary": health_dict,
        "allergies": allergen_list,
        "recommended_menus": [],
        "warnings": [],
        "blocked_menus": [],
        "alternatives": []
    }
    
    # 추천 메뉴
    for menu_id in recommendations.get("recommended", []):
        menu = next((m for m in menus if m.id == menu_id), None)
        if menu:
            result["recommended_menus"].append({
                "id": menu.id,
                "name": menu.name,
                "category": menu.category,
                "price": menu.price
            })
    
    # 경고 메뉴
    for warning in recommendations.get("warnings", []):
        menu = next((m for m in menus if m.id == warning["menu_id"]), None)
        if menu:
            result["warnings"].append({
                "id": menu.id,
                "name": menu.name,
                "reason": warning["reason"]
            })
    
    # 차단 메뉴
    for blocked in recommendations.get("blocked", []):
        menu = next((m for m in menus if m.id == blocked["menu_id"]), None)
        if menu:
            result["blocked_menus"].append({
                "id": menu.id,
                "name": menu.name,
                "reason": blocked["reason"]
            })
    
    # 대체 옵션
    for alt in recommendations.get("alternatives", []):
        menu = next((m for m in menus if m.id == alt["menu_id"]), None)
        if menu:
            result["alternatives"].append({
                "id": menu.id,
                "name": menu.name,
                "suggestion": alt["suggestion"]
            })
    
    return result
