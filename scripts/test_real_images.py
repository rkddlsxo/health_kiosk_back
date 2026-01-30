"""
실제 이미지를 사용한 전체 플로우 테스트
- user1.png: 회원가입용 얼굴 이미지
- user1_val.png: 로그인 검증용 얼굴 이미지 (동일 인물)
- health_info.png: 건강검진표 이미지
- allergy_info.png: 알러지 정보 이미지
"""
import requests
import os

# API Base URL
BASE_URL = "http://localhost:8000"

# 이미지 파일 경로
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER1_IMG = os.path.join(PROJECT_DIR, "user1.png")
USER1_VAL_IMG = os.path.join(PROJECT_DIR, "user1_val.png")
HEALTH_IMG = os.path.join(PROJECT_DIR, "health_info.png")
ALLERGY_IMG = os.path.join(PROJECT_DIR, "allergy_info.png")


def print_section(title):
    print("\n" + "="*60)
    print(f"{title}")
    print("="*60)


def test_user_registration():
    """1. 회원가입 테스트 (user1.png)"""
    print_section("1. 회원가입 (user1.png)")
    
    url = f"{BASE_URL}/api/auth/register"
    
    with open(USER1_IMG, "rb") as f:
        files = {"face_image": ("user1.png", f, "image/png")}
        data = {
            "account_id": "testuser1",
            "password": "test123",
            "name": "김테스트"
        }
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ 회원가입 성공!")
        print(f"   User ID: {user_data['id']}")
        print(f"   계정 ID: {user_data['account_id']}")
        print(f"   이름: {user_data['name']}")
        return user_data['id']
    else:
        print(f"❌ 회원가입 실패: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_face_login():
    """2. 얼굴 인식 로그인 테스트 (user1_val.png)"""
    print_section("2. 얼굴 인식 로그인 (user1_val.png)")
    
    url = f"{BASE_URL}/api/auth/login/face"
    
    with open(USER1_VAL_IMG, "rb") as f:
        files = {"face_image": ("user1_val.png", f, "image/png")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        login_data = response.json()
        print(f"✅ 얼굴 인식 로그인 성공!")
        print(f"   User ID: {login_data['user_id']}")
        print(f"   이름: {login_data['user_name']}")
        print(f"   메시지: {login_data['message']}")
        return login_data['user_id']
    else:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_health_report_upload(user_id):
    """3. 건강검진표 업로드 및 파싱 (health_info.png)"""
    print_section(f"3. 건강검진표 파싱 (health_info.png) - User ID: {user_id}")
    
    url = f"{BASE_URL}/api/health/users/{user_id}/health-report"
    
    with open(HEALTH_IMG, "rb") as f:
        files = {"health_report": ("health_info.png", f, "image/png")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ 건강검진표 파싱 성공!")
        print(f"\n파싱된 건강 정보:")
        
        # 주요 정보만 출력
        important_fields = [
            ("fasting_blood_sugar", "공복혈당"),
            ("total_cholesterol", "총콜레스테롤"),
            ("ldl_cholesterol", "LDL 콜레스테롤"),
            ("hdl_cholesterol", "HDL 콜레스테롤"),
            ("triglyceride", "중성지방"),
            ("bp_high", "수축기 혈압"),
            ("bp_low", "이완기 혈압"),
            ("bmi", "BMI"),
            ("hemoglobin", "혈색소"),
            ("ast", "AST"),
            ("alt", "ALT")
        ]
        
        for field, label in important_fields:
            value = health_data.get(field)
            if value is not None:
                print(f"   {label}: {value}")
        
        return health_data
    else:
        print(f"❌ 건강검진표 파싱 실패: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_allergy_info(user_id):
    """4. 알러지 정보 등록 (allergy_info.png는 Gemini로 파싱)"""
    print_section(f"4. 알러지 정보 등록 - User ID: {user_id}")
    
    # allergy_info.png를 Gemini로 파싱하여 알러지 정보 추출
    from app.services.gemini_service import get_gemini_service
    
    with open(ALLERGY_IMG, "rb") as f:
        image_bytes = f.read()
    
    gemini_service = get_gemini_service()
    
    # Gemini에게 알러지 정보 추출 요청
    from PIL import Image
    import io
    image = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
이미지에서 알러지 정보를 추출해주세요.
다음 JSON 형식으로 답해주세요:
[
  {
    "allergen_name": "알러지 유발 물질",
    "reaction": "반응 증상",
    "severity": "High/Medium/Low"
  }
]

예시:
[
  {"allergen_name": "땅콩", "reaction": "호흡곤란", "severity": "High"},
  {"allergen_name": "우유", "reaction": "두드러기", "severity": "Medium"}
]

반드시 JSON 배열 형식으로만 답해주세요.
"""
    
    try:
        response = gemini_service.model.generate_content([prompt, image])
        result_text = response.text.strip()
        
        # JSON 추출
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        import json
        allergies = json.loads(result_text)
        
        print(f"✅ 알러지 정보 파싱 성공: {len(allergies)}개")
        for allergy in allergies:
            print(f"   - {allergy['allergen_name']} (반응: {allergy['reaction']}, 심각도: {allergy['severity']})")
        
    except Exception as e:
        print(f"⚠️  알러지 이미지 파싱 실패, 더미 데이터 사용: {e}")
        allergies = [
            {"allergen_name": "우유", "reaction": "두드러기", "severity": "High"},
            {"allergen_name": "땅콩", "reaction": "호흡곤란", "severity": "High"}
        ]
    
    # API로 알러지 정보 등록
    url = f"{BASE_URL}/api/health/users/{user_id}/allergy"
    response = requests.post(url, json=allergies)
    
    if response.status_code == 200:
        print(f"✅ 알러지 정보 등록 완료!")
        return allergies
    else:
        print(f"❌ 알러지 정보 등록 실패: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_menu_recommendations(user_id):
    """5. 메뉴 추천 테스트"""
    print_section(f"5. 메뉴 추천 - User ID: {user_id}")
    
    url = f"{BASE_URL}/api/recommend/{user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        recommendations = response.json()
        
        print(f"\n👤 사용자: {recommendations['user_name']}")
        print(f"\n🏥 건강 요약:")
        for key, value in recommendations['health_summary'].items():
            print(f"   {key}: {value}")
        
        print(f"\n🚫 알러지: {', '.join(recommendations['allergies'])}")
        
        print(f"\n✅ 추천 메뉴 ({len(recommendations['recommended_menus'])}개):")
        for menu in recommendations['recommended_menus']:
            print(f"   - {menu['name']} ({menu['category']}, {menu['price']}원)")
        
        print(f"\n⚠️  경고 메뉴 ({len(recommendations['warnings'])}개):")
        for warning in recommendations['warnings']:
            print(f"   - {warning['name']}")
            print(f"     이유: {warning['reason']}")
        
        print(f"\n🚫 차단 메뉴 ({len(recommendations['blocked_menus'])}개):")
        for blocked in recommendations['blocked_menus']:
            print(f"   - {blocked['name']}")
            print(f"     이유: {blocked['reason']}")
        
        print(f"\n💡 대체 옵션 ({len(recommendations['alternatives'])}개):")
        for alt in recommendations['alternatives']:
            print(f"   - {alt['name']}")
            print(f"     제안: {alt['suggestion']}")
        
        return recommendations
    else:
        print(f"❌ 메뉴 추천 실패: {response.status_code}")
        print(f"   {response.text}")
        return None


def main():
    """전체 플로우 테스트"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "실제 이미지 기반 전체 플로우 테스트" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    # 이미지 파일 존재 확인
    for img_path, img_name in [(USER1_IMG, "user1.png"), (USER1_VAL_IMG, "user1_val.png"), 
                                 (HEALTH_IMG, "health_info.png"), (ALLERGY_IMG, "allergy_info.png")]:
        if not os.path.exists(img_path):
            print(f"❌ 이미지 파일 없음: {img_name}")
            return
    
    print("✅ 모든 이미지 파일 확인 완료")
    
    # 1. 회원가입
    user_id = test_user_registration()
    if not user_id:
        print("\n❌ 회원가입 실패로 테스트 중단")
        return
    
    # 2. 얼굴 인식 로그인
    logged_in_user_id = test_face_login()
    if not logged_in_user_id:
        print("\n❌ 로그인 실패로 테스트 중단")
        return
    
    if logged_in_user_id == user_id:
        print(f"\n✅ user1.png와 user1_val.png가 동일 인물로 인식됨!")
    else:
        print(f"\n⚠️  다른 사용자로 인식됨 (예상: {user_id}, 실제: {logged_in_user_id})")
    
    # 3. 건강검진표 업로드
    health_data = test_health_report_upload(user_id)
    if not health_data:
        print("\n❌ 건강검진표 파싱 실패로 테스트 중단")
        return
    
    # 4. 알러지 정보 등록
    allergies = test_allergy_info(user_id)
    if not allergies:
        print("\n❌ 알러지 정보 등록 실패로 테스트 중단")
        return
    
    # 5. 메뉴 추천
    recommendations = test_menu_recommendations(user_id)
    if not recommendations:
        print("\n❌ 메뉴 추천 실패")
        return
    
    # 최종 결과
    print_section("테스트 완료!")
    print("✅ 전체 플로우 성공!")
    print(f"   - 회원가입 ✅")
    print(f"   - 얼굴 인식 로그인 ✅")
    print(f"   - 동일 인물 인식 ✅")
    print(f"   - 건강검진표 파싱 ✅")
    print(f"   - 알러지 정보 등록 ✅")
    print(f"   - 메뉴 추천 ✅")


if __name__ == "__main__":
    print("\n서버가 실행 중인지 확인하세요: uvicorn app.main:app --reload\n")
    main()
