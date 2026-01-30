"""
API 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print(" 서버 연결 테스트")
print("="*60)

# 1. 서버 상태 확인
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"\n✅ 서버 응답: {response.json()}")
except Exception as e:
    print(f"\n❌ 서버 연결 실패: {e}")
    exit(1)

# 2. 회원가입 테스트
print("\n" + "="*60)
print(" 회원가입 테스트")
print("="*60)

user_data = {
    "account_id": "test123",
    "password": "test1234",
    "name": "테스트유저"
}

try:
    response = requests.post(f"{BASE_URL}/user/register", json=user_data)
    if response.status_code == 200:
        print(f"\n✅ 회원가입 성공!")
        print(f"   응답: {response.json()}")
    else:
        print(f"\n⚠️  회원가입 응답: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"\n❌ 회원가입 실패: {e}")

# 3. 로그인 테스트
print("\n" + "="*60)
print(" 로그인 테스트")
print("="*60)

login_data = {
    "account_id": "test123",
    "password": "test1234"
}

try:
    response = requests.post(f"{BASE_URL}/user/login", json=login_data)
    if response.status_code == 200:
        print(f"\n✅ 로그인 성공!")
        print(f"   응답: {response.json()}")
    else:
        print(f"\n⚠️  로그인 응답: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"\n❌ 로그인 실패: {e}")

print("\n" + "="*60)
print(" 테스트 완료!")
print(f" API 문서: {BASE_URL}/docs")
print("="*60)
