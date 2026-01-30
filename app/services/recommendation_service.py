"""
메뉴 추천 비즈니스 로직 및 캐싱 서비스
"""
import json
import time
from sqlalchemy.orm import Session
from app.models import User, UserHealth, UserAllergy, Menu
from app.services.gemini_service import get_gemini_service

from app.database import SessionLocal

def update_user_recommendation(user_id: int, db: Session = None):
    """
    백그라운드 작업용: 추천 결과를 계산하여 DB에 저장
    주의: BackgroundTasks에서 호출될 때는 db 세션이 이미 닫혔을 수 있으므로,
    새로운 세션을 직접 생성해서 사용해야 함.
    """
    
    # 세션 관리 (외부에서 주입받았으면 그거 쓰고, 아니면 새로 생성)
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True
        
    start_time = time.time()
    print(f"\n[DEBUG] ===============================================")
    print(f"[DEBUG] User {user_id} 추천 데이터 계산 시작 (Background Task)")
    print(f"[DEBUG] ===============================================")
    
    try:
        result = calculate_recommendations(user_id, db)
        
        if result:
            # JSON 직렬화하여 저장
            # 주의: calculate_recommendations에서 조회한 user 객체는 해당 세션에 종속됨
            # 만약 calculate 내부에서 세션을 썼다면 그 세션으로 commit 해야 함
            
            # 재조회 (확실하게 하기 위함)
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.recommendation_cache = json.dumps(result, ensure_ascii=False)
                db.commit()
                elapsed = time.time() - start_time
                print(f"[DEBUG] ✅ User {user_id} 추천 데이터 DB 캐싱 완료! (소요시간: {elapsed:.2f}초)")
            else:
                 print(f"[DEBUG] ❌ User {user_id} 찾을 수 없음 (DB Commit 실패)")
                 
            print(f"[DEBUG] ===============================================\n")
        else:
            print(f"[DEBUG] ❌ User {user_id} 추천 데이터 계산 실패 (결과 없음)")
            print(f"[DEBUG] ===============================================\n")
            
    except Exception as e:
        print(f"[DEBUG] 💥 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        print(f"[DEBUG] ===============================================\n")
    finally:
        if own_session:
            db.close()

def calculate_recommendations(user_id: int, db: Session):
    """
    사용자의 건강/알러지 정보를 기반으로 메뉴 추천 결과를 계산합니다.
    """
    print(f"[DEBUG] >> 사용자 정보 및 메뉴 데이터 로딩 중...")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"[DEBUG] 사용자(ID: {user_id})를 찾을 수 없음")
        return None
    
    # 건강 정보
    health = db.query(UserHealth).filter(UserHealth.user_id == user_id).first()
    if not health:
        print(f"[DEBUG] 사용자(ID: {user_id}) 건강 정보 없음")
        return _create_empty_result(user.name)

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

    # 알러지 정보
    allergies = db.query(UserAllergy).filter(UserAllergy.user_id == user_id).all()
    allergen_list = [allergy.allergen_name for allergy in allergies]

    # 메뉴 리스트
    menus = db.query(Menu).all()
    menu_list = []
    for menu in menus:
        menu_dict = {
            "id": menu.id,
            "name": menu.name,
            "category": menu.category,
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

    # ---------------------------------------------------------
    # 1. 룰 베이스 필터링 (알레르기)
    # ---------------------------------------------------------
    print(f"[DEBUG] >> 1단계: 룰 베이스 필터링 (알레르기) 시작...")
    safe_menus = []
    allergy_blocked_menus = []

    for menu in menu_list:
        matched_allergens = []
        
        if menu.get("allergens"):
            menu_allergens = [a.strip() for a in menu["allergens"].split(",")]
            for user_allergen in allergen_list:
                for ma in menu_allergens:
                     # 부분 일치 확인 (예: 땅콩 <-> 땅콩가루)
                    if user_allergen in ma or ma in user_allergen:
                        matched_allergens.append(f"{user_allergen}({ma})")

        if matched_allergens:
            # 중복 제거
            matched_allergens = list(set(matched_allergens))
            blocked_reason = ", ".join(matched_allergens) + " 함유"
            
            # DB애서 메뉴 정보 다시 조회
            m_obj = next((m for m in menus if m.id == menu["id"]), None)
            if m_obj:
                allergy_blocked_menus.append({
                    "id": m_obj.id,
                    "name": m_obj.name,
                    "category": m_obj.category,
                    "price": m_obj.price,
                    "image_url": m_obj.image_url,
                    "reason": blocked_reason
                })
        else:
            safe_menus.append(menu)

    print(f"[DEBUG] >> 알레르기 필터링 결과: 안전 메뉴 {len(safe_menus)}개 / 차단 메뉴 {len(allergy_blocked_menus)}개")

    # ---------------------------------------------------------
    # 2. AI 추천 실행
    # ---------------------------------------------------------
    gemini_service = get_gemini_service()
    
    try:
        print(f"[DEBUG] >> 2단계: Gemini AI 분석 요청 시작... (대상 메뉴: {len(safe_menus)}개)")
        ai_start = time.time()

        # 안전한 메뉴만 전달
        if not safe_menus:
             print(f"[DEBUG] 안전한 메뉴가 없어 AI 추천 스킵")
             recommendations_from_ai = {}
        else:
            recommendations_from_ai = gemini_service.generate_menu_recommendations(
                health_data=health_dict,
                allergens=allergen_list,
                menus=safe_menus
            )
        ai_elapsed = time.time() - ai_start
        print(f"[DEBUG] >> Gemini 응답 수신 완료 (API 소요시간: {ai_elapsed:.2f}초)")
        
    except Exception as e:
        print(f"[DEBUG] ** Gemini API 호출 중 오류 발생: {e}")
        recommendations_from_ai = {
            "recommended": [],
            "blocked_health": []
        }
    
    # ---------------------------------------------------------
    # 3. 결과 통합
    # ---------------------------------------------------------
    result = {
        "user_name": user.name,
        "health_summary": health_dict,
        "allergies": allergen_list,
        "recommended_menus": [],
        "normal_menus": [],
        "allergy_menus": allergy_blocked_menus,
        "health_menus": []
    }
    
    ai_reco_list = recommendations_from_ai.get("recommended", [])
    ai_blocked_health_list = recommendations_from_ai.get("blocked_health", [])
    
    # 아이디 추출 (방어 코드 적용)
    reco_ids = []
    for item in ai_reco_list:
        if isinstance(item, dict):
            reco_ids.append(item.get("menu_id"))
        elif isinstance(item, int):
            reco_ids.append(item)
            
    health_blocked_ids = []
    for item in ai_blocked_health_list:
        if isinstance(item, dict):
            health_blocked_ids.append(item.get("menu_id"))
        elif isinstance(item, int):
            health_blocked_ids.append(item)

    # (1) Recommended
    for item in ai_reco_list:
        # 데이터 정규화
        if isinstance(item, int):
            menu_id = item
            reason = "건강 맞춤 추천"
            options = []
        else:
            menu_id = item.get("menu_id")
            reason = item.get("reason", "건강 맞춤 추천")
            options = item.get("selected_options", [])
            
        
        menu_obj = next((m for m in menus if m.id == menu_id), None)
        
        # [Fallback] AI가 옵션을 안 줬는데 건강 이슈가 있다면 강제 주입 (Trick)
        if not options:
            if health_dict.get("fasting_blood_sugar", 0) >= 100:
                options.append("덜 달게")
            if health_dict.get("bp_high", 0) >= 130:
                options.append("디카페인")
            # 노인 배려 기본 옵션
            if menu_obj and "tea" in (menu_obj.category or "").lower():
                    options.append("따뜻하게")
        
        if menu_obj:
            result["recommended_menus"].append({
                "id": menu_obj.id,
                "name": menu_obj.name,
                "category": menu_obj.category,
                "price": menu_obj.price,
                "image_url": menu_obj.image_url,
                "selected_options": options,
                "reason": reason

            })

    # [Demo Logic] 만약 추천 메뉴는 있는데 옵션이 하나도 없다면? -> 첫 번째 메뉴에 강제 주입
    if result["recommended_menus"] and not any(m["selected_options"] for m in result["recommended_menus"]):
        target = result["recommended_menus"][0]
        name_lower = (target["name"] or "").lower()
        cat_lower = (target["category"] or "").lower()
        
        forced_option = "따뜻하게" # Default
        
        # 품목별 적절한 옵션 매핑
        if "아이스" in name_lower or "ice" in name_lower or "smoothie" in cat_lower or "ade" in cat_lower:
            forced_option = "얼음 적게"
        elif "cake" in cat_lower or "dessert" in cat_lower or "breadcrumb" in cat_lower or "케이크" in name_lower:
            forced_option = "먹기 좋게 커팅"
        elif "coffee" in cat_lower or "커피" in name_lower:
            forced_option = "연하게"
        elif "tea" in cat_lower or "티" in name_lower:
            forced_option = "따뜻하게"
        elif "juice" in cat_lower or "주스" in name_lower:
            forced_option = "시럽 없이"
            
        target["selected_options"].append(forced_option)

    # (2) Health Blocked
    for item in ai_blocked_health_list:
        if isinstance(item, int):
            menu_id = item
            reason = "건강상 주의 필요"
        else:
            menu_id = item.get("menu_id")
            reason = item.get("reason", "건강상 주의 필요")
            
        menu_obj = next((m for m in menus if m.id == menu_id), None)
        if menu_obj:
            result["health_menus"].append({
                "id": menu_obj.id,
                "name": menu_obj.name,
                "category": menu_obj.category,
                "price": menu_obj.price,
                "image_url": menu_obj.image_url,
                "reason": reason
            })
            
    # (3) Normal
    for menu_dict in safe_menus:
        m_id = menu_dict["id"]
        if m_id not in reco_ids and m_id not in health_blocked_ids:
            menu_obj = next((m for m in menus if m.id == m_id), None)
            if menu_obj:
                result["normal_menus"].append({
                    "id": menu_obj.id,
                    "name": menu_obj.name,
                    "category": menu_obj.category,
                    "price": menu_obj.price,
                    "image_url": menu_obj.image_url
                })
                
    return result

def _create_empty_result(user_name):
    return {
        "user_name": user_name,
        "health_summary": {},
        "allergies": [],
        "recommended_menus": [],
        "normal_menus": [],
        "allergy_menus": [],
        "health_menus": []
    }
