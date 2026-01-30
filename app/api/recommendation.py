"""
메뉴 추천 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.recommendation_service import calculate_recommendations
import json

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
    
    # 1. 캐시 확인
    if user.recommendation_cache:
        try:
            print(f"User {user_id}: 캐시된 추천 데이터 반환")
            return json.loads(user.recommendation_cache)
        except Exception:
            print("캐시 데이터 파싱 오류, 재생성 진행")
            
    # 2. 캐시 없으면 실시간 계산
    print(f"User {user_id}: 추천 데이터 실시간 계산 중...")
    result = calculate_recommendations(user_id, db)
    
    if not result:
        # 건강 정보가 전혀 없는 경우 등
        return {
            "user_name": user.name,
            "recommended_menus": [],
            "normal_menus": [],
            "allergy_menus": [],
            "health_menus": []
        }
        
    # 실시간 계산 결과 저장 (다음 요청을 위해)
    user.recommendation_cache = json.dumps(result, ensure_ascii=False)
    db.commit()
    
    return result
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
            "ingredients": None, # base_ingredients 컬럼 사라짐 -> None 처리 또는 제거
            "allergens": menu.allergens,
            "nutrition": {
                "sugar": menu.sugar,
                "fat": menu.fat,
                "calories": menu.calories,
                "protein": menu.protein,
                "sodium": menu.sodium,
                "carbs": menu.carbs
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

    # ---------------------------------------------------------
    # 1단계: Rule-based Filtering (알레르기)
    # ---------------------------------------------------------
    safe_menus = []
    allergy_blocked_menus = []

    for menu in menu_list:
        is_allergy_risk = False
        blocked_reason = ""
        
        # 메뉴의 알레르기 유발 물질 확인 (DB 컬럼: allergens, 예: "우유,대두")
        if menu.get("allergens"):
            menu_allergens = [a.strip() for a in menu["allergens"].split(",")]
            # 사용자 알레르기와 매칭
            for user_allergen in allergen_list:
                # 부분 일치도 위험 (예: '우유' vs '우유단백질') 또는 정확 일치
                # 간단하게 포함 여부로 체크
                for ma in menu_allergens:
                    if user_allergen in ma or ma in user_allergen:
                        is_allergy_risk = True
                        blocked_reason = f"{user_allergen} 알레르기 위험"
                        break
                if is_allergy_risk:
                    break
        
        if is_allergy_risk:
            allergy_blocked_menus.append({
                "id": menu["id"],
                "name": menu["name"],
                "category": menu["category"],
                "price": 0, # 필요 시 DB 조회
                "image_url": "", # 필요 시
                "reason": blocked_reason
            })
        else:
            safe_menus.append(menu)

    # ---------------------------------------------------------
    # 2단계: AI Recommendation (건강 분석 + 옵션 자동화)
    # ---------------------------------------------------------
    gemini_service = get_gemini_service()
    
    # AI에게는 '안전한 메뉴(safe_menus)'만 전달하여 건강 분석을 요청
    recommendations_from_ai = gemini_service.generate_menu_recommendations(
        health_data=health_dict,
        allergens=allergen_list, # 참고용으로 전달
        menus=safe_menus
    )
    
    # ---------------------------------------------------------
    # 3단계: 결과 통합 및 분류
    # ---------------------------------------------------------
    
    # 최종 반환 구조
    result = {
        "user_name": user.name,
        "health_summary": health_dict,
        "allergies": allergen_list,
        
        "recommended_menus": [],    # AI 추천 Top 2 (옵션 포함)
        "normal_menus": [],         # 문제없는 일반 메뉴
        "allergy_menus": [],        # 알레르기 차단 메뉴
        "health_menus": []          # 건강상 위험 메뉴 (AI 판단)
    }
    
    # 1. 알레르기 차단 메뉴 (Rule)
    # DB에서 가격 정보 등을 다시 가져오기 위해 ID 매핑
    for blocked in allergy_blocked_menus:
         menu = next((m for m in menus if m.id == blocked["id"]), None)
         if menu:
             result["allergy_menus"].append({
                 "id": menu.id,
                 "name": menu.name,
                 "category": menu.category,
                 "price": menu.price,
                 "image_url": menu.image_url,
                 "reason": blocked["reason"]
             })

    # 2. AI 결과 처리
    ai_reco_list = recommendations_from_ai.get("recommended", [])
    ai_blocked_health_list = recommendations_from_ai.get("blocked_health", [])
    
    reco_ids = [item["menu_id"] for item in ai_reco_list]
    health_blocked_ids = [item["menu_id"] for item in ai_blocked_health_list]
    
    # (1) Recommended Menus
    for item in ai_reco_list:
        menu_id = item["menu_id"]
        menu = next((m for m in menus if m.id == menu_id), None)
        if menu:
            result["recommended_menus"].append({
                "id": menu.id,
                "name": menu.name,
                "category": menu.category,
                "price": menu.price,
                "image_url": menu.image_url,
                "selected_options": item.get("selected_options", []),
                "reason": item.get("reason", "건강 맞춤 추천")
            })
            
    # (2) Health Blocked Menus
    for item in ai_blocked_health_list:
        menu_id = item["menu_id"]
        menu = next((m for m in menus if m.id == menu_id), None)
        if menu:
            result["health_menus"].append({
                "id": menu.id,
                "name": menu.name,
                "category": menu.category,
                "price": menu.price,
                "image_url": menu.image_url,
                "reason": item.get("reason", "건강상 주의 필요")
            })
            
    # (3) Normal Menus
    # Safe Menus 중에서 (Recommended도 아니고) (Health Blocked도 아닌) 나머지
    for menu_dict in safe_menus:
        m_id = menu_dict["id"]
        if m_id not in reco_ids and m_id not in health_blocked_ids:
            menu = next((m for m in menus if m.id == m_id), None)
            if menu:
                result["normal_menus"].append({
                    "id": menu.id,
                    "name": menu.name,
                    "category": menu.category,
                    "price": menu.price,
                    "image_url": menu.image_url
                })
    
    return result
