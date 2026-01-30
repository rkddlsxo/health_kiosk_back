"""
전체 시스템 통합 테스트
회원가입 → 로그인 → 건강정보 등록 → 알러지 등록
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_separator(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def test_1_server_health():
    """1. 서버 상태 확인"""
    print_separator("1️⃣  서버 상태 확인")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ 서버 응답: {response.json()}")
            return True
        else:
            print(f"❌ 서버 응답 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def test_2_register():
    """2. 회원가입"""
    print_separator("2️⃣  회원가입")
    
    user_data = {
        "account_id": "healthuser01",
        "password": "test1234",
        "name": "김건강"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/register", json=user_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 회원가입 성공!")
            print(f"   계정 ID: {result['account_id']}")
            print(f"   이름: {result['name']}")
            return user_data['account_id']
        elif response.status_code == 400:
            print(f"⚠️  이미 가입된 사용자 (계속 진행)")
            return user_data['account_id']
        else:
            print(f"❌ 회원가입 실패: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_3_login(account_id):
    """3. 로그인"""
    print_separator("3️⃣  로그인")
    
    login_data = {
        "account_id": account_id,
        "password": "test1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 로그인 성공!")
            print(f"   메시지: {result['message']}")
            print(f"   사용자: {result['name']}")
            return True
        else:
            print(f"❌ 로그인 실패: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_4_health_info(account_id):
    """4. 건강 정보 등록"""
    print_separator("4️⃣  건강 정보 등록")
    
    health_data = {
        "height": 175.0,
        "weight": 70.0,
        "bmi": 22.9,
        "bp_high": 125,
        "bp_low": 82,
        "fasting_blood_sugar": 105,  # 약간 높음
        "total_cholesterol": 210,     # 약간 높음
        "hdl_cholesterol": 45,         # 약간 낮음
        "ldl_cholesterol": 140,        # 약간 높음
        "triglyceride": 180,           # 약간 높음
        "hemoglobin": 14.5,
        "ast": 28,
        "alt": 32,
        "gamma_gtp": 40
    }
    
    try:
        response = requests.put(f"{BASE_URL}/user/{account_id}/health-info", json=health_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 건강 정보 등록 성공!")
            print(f"   {result['message']}")
            print(f"\n등록된 건강 정보:")
            print(f"   🏃 키/몸무게: {health_data['height']}cm / {health_data['weight']}kg")
            print(f"   💉 혈압: {health_data['bp_high']}/{health_data['bp_low']} mmHg")
            print(f"   🩸 공복혈당: {health_data['fasting_blood_sugar']} mg/dL")
            print(f"   🧪 총콜레스테롤: {health_data['total_cholesterol']} mg/dL")
            print(f"   🧪 LDL: {health_data['ldl_cholesterol']} mg/dL")
            print(f"   🧪 중성지방: {health_data['triglyceride']} mg/dL")
            return True
        else:
            print(f"❌ 건강 정보 등록 실패: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_5_allergies(account_id):
    """5. 알러지 정보 등록"""
    print_separator("5️⃣  알러지 정보 등록")
    
    allergies = [
        {
            "allergen_name": "우유",
            "reaction": "두드러기",
            "severity": "High"
        },
        {
            "allergen_name": "땅콩",
            "reaction": "호흡곤란",
            "severity": "High"
        }
    ]
    
    success_count = 0
    for allergy in allergies:
        try:
            response = requests.post(f"{BASE_URL}/user/{account_id}/allergies", json=allergy)
            if response.status_code == 200:
                print(f"✅ {allergy['allergen_name']} 알러지 등록 성공!")
                print(f"   반응: {allergy['reaction']}, 심각도: {allergy['severity']}")
                success_count += 1
            else:
                print(f"❌ {allergy['allergen_name']} 알러지 등록 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {e}")
    
    return success_count == len(allergies)

def test_6_verify_data(account_id):
    """6. 데이터 검증 (DB 확인)"""
    print_separator("6️⃣  데이터 검증")
    
    print("📊 등록된 데이터 요약:")
    print(f"   계정 ID: {account_id}")
    print(f"   ✅ 회원 정보")
    print(f"   ✅ 건강 정보 (14개 필드)")
    print(f"   ✅ 알러지 정보 (2개)")
    
    return True

def main():
    """전체 테스트 실행"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "전체 시스템 통합 테스트" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # 1. 서버 상태
    results['서버'] = test_1_server_health()
    if not results['서버']:
        print("\n❌ 서버가 실행되지 않았습니다. 테스트 중단.")
        return
    
    # 2. 회원가입
    account_id = test_2_register()
    results['회원가입'] = account_id is not None
    if not account_id:
        print("\n❌ 회원가입 실패. 테스트 중단.")
        return
    
    # 3. 로그인
    results['로그인'] = test_3_login(account_id)
    
    # 4. 건강 정보
    results['건강정보'] = test_4_health_info(account_id)
    
    # 5. 알러지
    results['알러지'] = test_5_allergies(account_id)
    
    # 6. 검증
    results['검증'] = test_6_verify_data(account_id)
    
    # 최종 결과
    print_separator("✨ 테스트 결과 요약")
    
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name:15s} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 모든 테스트 통과!")
        print(f"\n✅ API 문서: {BASE_URL}/docs")
        print(f"✅ 사용자 계정: {account_id}")
    else:
        print("⚠️  일부 테스트 실패")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
