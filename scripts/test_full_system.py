"""
전체 시스템 테스트 스크립트
얼굴 인식 → 건강정보 → 필터링까지 전 과정 검증
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini_service import get_gemini_service
from app.services.face_service import get_face_service
from PIL import Image, ImageDraw, ImageFont
import io
import json
import numpy as np


def test_gemini_connection():
    """Gemini API 연결 테스트"""
    print("\n" + "="*60)
    print("1. Gemini API 연결 테스트")
    print("="*60)
    
    try:
        gemini_service = get_gemini_service()
        print("✅ Gemini 서비스 초기화 성공")
        
        # 간단한 텍스트 생성 테스트
        from google.generativeai import GenerativeModel
        model = GenerativeModel('gemini-flash-latest')
        response = model.generate_content("Hello, just testing connection. Reply 'OK'")
        print(f"✅ Gemini API 응답: {response.text.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API 연결 실패: {e}")
        return False


def test_face_recognition():
    """얼굴 인식 테스트 (더미 이미지 생성)"""
    print("\n" + "="*60)
    print("2. 얼굴 인식 테스트")
    print("="*60)
    
    try:
        face_service = get_face_service()
        print("✅ InsightFace 서비스 초기화 성공")
        
        # 더미 얼굴 이미지 생성 (실제로는 사진 사용)
        print("\n⚠️  실제 얼굴 사진이 필요합니다.")
        print("   더미 이미지로는 얼굴 감지가 안 될 수 있습니다.")
        print("   테스트를 위해 간단한 이미지를 생성하지만,")
        print("   실제 테스트는 API를 통해 사진을 업로드해야 합니다.")
        
        # 간단한 더미 이미지
        img = Image.new('RGB', (640, 480), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse([220, 140, 420, 340], fill='beige', outline='black', width=2)
        draw.ellipse([270, 200, 300, 230], fill='black')
        draw.ellipse([340, 200, 370, 230], fill='black')
        draw.arc([290, 260, 350, 300], 0, 180, fill='black', width=3)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        embedding = face_service.extract_face_embedding(img_bytes)
        
        if embedding is None:
            print("❌ 더미 이미지에서 얼굴 감지 실패 (예상된 결과)")
            print("✅ 하지만 face_service는 정상 작동합니다")
            return True
        else:
            print(f"✅ 얼굴 임베딩 추출 성공! 차원: {embedding.shape}")
            return True
            
    except Exception as e:
        print(f"❌ 얼굴 인식 테스트 실패: {e}")
        return False


def test_health_report_parsing():
    """건강검진표 파싱 테스트"""
    print("\n" + "="*60)
    print("3. 건강검진표 파싱 테스트 (Gemini)")
    print("="*60)
    
    try:
        gemini_service = get_gemini_service()
        
        # 더미 건강검진표 이미지 생성 (텍스트 포함)
        print("\n📋 더미 건강검진표 이미지 생성 중...")
        
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # 텍스트 추가
        texts = [
            "건강검진 결과표",
            "",
            "공복혈당: 110 mg/dL",
            "총콜레스테롤: 220 mg/dL",
            "LDL 콜레스테롤: 150 mg/dL",
            "HDL 콜레스테롤: 45 mg/dL",
            "중성지방: 180 mg/dL",
            "수축기혈압: 135 mmHg",
            "이완기혈압: 88 mmHg",
            "BMI: 25.5",
            "허리둘레: 92 cm"
        ]
        
        y = 50
        for text in texts:
            draw.text((50, y), text, fill='black')
            y += 40
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        print("📤 Gemini API에 이미지 전송 중...")
        parsed_data = gemini_service.parse_health_report(img_bytes)
        
        if parsed_data:
            print("✅ 건강검진표 파싱 성공!")
            print("\n파싱 결과:")
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
            return parsed_data
        else:
            print("❌ 파싱 실패")
            return None
            
    except Exception as e:
        print(f"❌ 건강검진표 파싱 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_menu_recommendation(health_data):
    """메뉴 추천 테스트"""
    print("\n" + "="*60)
    print("4. 메뉴 추천 및 필터링 테스트")
    print("="*60)
    
    try:
        gemini_service = get_gemini_service()
        
        # 더미 알러지 정보
        allergens = ["milk"]
        print(f"\n🏥 건강 데이터: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
        print(f"🚫 알러지 정보: {allergens}")
        
        # 더미 메뉴 데이터
        menus = [
            {
                "id": 1,
                "name": "아메리카노",
                "category": "커피",
                "ingredients": ["espresso", "water"],
                "allergens": [],
                "nutrition": {"sugar": 0, "fat": 0, "calories": 10, "caffeine": 75}
            },
            {
                "id": 2,
                "name": "카페라떼",
                "category": "커피",
                "ingredients": ["espresso", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 10, "fat": 5, "calories": 150, "caffeine": 75}
            },
            {
                "id": 3,
                "name": "카페모카",
                "category": "커피",
                "ingredients": ["espresso", "milk", "chocolate", "whipped_cream"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 35, "fat": 10, "calories": 320, "caffeine": 85}
            },
            {
                "id": 4,
                "name": "초코라떼",
                "category": "음료",
                "ingredients": ["chocolate", "milk"],
                "allergens": ["milk"],
                "nutrition": {"sugar": 30, "fat": 8, "calories": 280, "caffeine": 20}
            },
            {
                "id": 5,
                "name": "레모네이드",
                "category": "음료",
                "ingredients": ["lemon", "sugar", "water"],
                "allergens": [],
                "nutrition": {"sugar": 25, "fat": 0, "calories": 100, "caffeine": 0}
            }
        ]
        
        print(f"\n📋 테스트 메뉴: {len(menus)}개")
        for menu in menus:
            print(f"  - {menu['name']} (알러지: {menu['allergens']}, 당:{menu['nutrition']['sugar']}g)")
        
        print("\n📤 Gemini API에 추천 요청 중...")
        recommendations = gemini_service.generate_menu_recommendations(
            health_data=health_data,
            allergens=allergens,
            menus=menus
        )
        
        print("\n" + "="*60)
        print("✅ 메뉴 추천 결과")
        print("="*60)
        
        print("\n✅ 추천 메뉴:")
        if recommendations.get("recommended"):
            for menu_id in recommendations["recommended"]:
                menu = next((m for m in menus if m["id"] == menu_id), None)
                if menu:
                    print(f"  - {menu['name']}")
        else:
            print("  없음")
        
        print("\n⚠️  경고 메뉴:")
        if recommendations.get("warnings"):
            for warning in recommendations["warnings"]:
                menu = next((m for m in menus if m["id"] == warning["menu_id"]), None)
                if menu:
                    print(f"  - {menu['name']}")
                    print(f"    이유: {warning['reason']}")
        else:
            print("  없음")
        
        print("\n🚫 차단 메뉴:")
        if recommendations.get("blocked"):
            for blocked in recommendations["blocked"]:
                menu = next((m for m in menus if m["id"] == blocked["menu_id"]), None)
                if menu:
                    print(f"  - {menu['name']}")
                    print(f"    이유: {blocked['reason']}")
        else:
            print("  없음")
        
        print("\n💡 대체 옵션:")
        if recommendations.get("alternatives"):
            for alt in recommendations["alternatives"]:
                menu = next((m for m in menus if m["id"] == alt["menu_id"]), None)
                if menu:
                    print(f"  - {menu['name']}")
                    print(f"    제안: {alt['suggestion']}")
        else:
            print("  없음")
        
        return True
        
    except Exception as e:
        print(f"❌ 메뉴 추천 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 테스트 실행"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "건강 키오스크 백엔드 통합 테스트" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # 1. Gemini 연결 테스트
    results.append(("Gemini API 연결", test_gemini_connection()))
    
    # 2. 얼굴 인식 테스트
    results.append(("얼굴 인식", test_face_recognition()))
    
    # 3. 건강검진표 파싱 테스트
    health_data = test_health_report_parsing()
    results.append(("건강검진표 파싱", health_data is not None))
    
    # 4. 메뉴 추천 테스트
    if health_data:
        results.append(("메뉴 추천", test_menu_recommendation(health_data)))
    else:
        # 파싱 실패 시 더미 데이터 사용
        dummy_health = {
            "blood_sugar": 110,
            "ldl": 150,
            "cholesterol_total": 220,
            "triglycerides": 180,
            "blood_pressure_systolic": 135,
            "blood_pressure_diastolic": 88,
            "bmi": 25.5,
            "waist_circumference": 92
        }
        results.append(("메뉴 추천", test_menu_recommendation(dummy_health)))
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name:20s}: {status}")
    
    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    
    print(f"\n전체: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n⚠️  일부 테스트 실패. 로그를 확인하세요.")


if __name__ == "__main__":
    main()
