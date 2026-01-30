"""
Gemini API 연동 서비스
"""
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Optional, Dict, Any
from PIL import Image
import io
import json
from app.config import get_settings

settings = get_settings()


class GeminiService:
    """Gemini API 서비스 클래스"""
    
    def __init__(self):
        """Gemini API 초기화"""
        genai.configure(api_key=settings.gemini_api_key)
        
        # 모델 설정
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
    
    def parse_health_report(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        건강검진표 이미지를 파싱하여 구조화된 JSON 반환
        
        Args:
            image_bytes: 건강검진표 이미지 바이트 데이터
            
        Returns:
            파싱된 건강 정보 딕셔너리
        """
        # 바이트를 PIL Image로 변환
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
다음은 건강검진표 이미지입니다. 아래 항목들을 찾아서 JSON 형식으로 추출해주세요.
찾을 수 없는 항목은 null로 표시하세요.

추출할 항목:

[계측 검사]
- height: 신장 (cm, 숫자만)
- weight: 체중 (kg, 숫자만)
- waist: 허리둘레 (cm, 숫자만)
- bmi: 체질량지수 (숫자만)
- vision_l: 시력 좌 (숫자만)
- vision_r: 시력 우 (숫자만)
- hearing_l: 청력 좌 (텍스트, 예: "정상", "비정상")
- hearing_r: 청력 우 (텍스트)
- bp_high: 수축기 혈압/최고혈압 (mmHg, 숫자만)
- bp_low: 이완기 혈압/최저혈압 (mmHg, 숫자만)

[요검사]
- urine_protein: 요단백 (텍스트, 예: "음성", "양성")

[혈액 검사]
- hemoglobin: 혈색소/빈혈 (g/dL, 숫자만)
- fasting_blood_sugar: 식전혈당/공복혈당 (mg/dL, 숫자만)
- total_cholesterol: 총콜레스테롤 (mg/dL, 숫자만)
- hdl_cholesterol: HDL 콜레스테롤 (mg/dL, 숫자만)
- triglyceride: 중성지방 (mg/dL, 숫자만)
- ldl_cholesterol: LDL 콜레스테롤 (mg/dL, 숫자만)
- creatinine: 혈청크레아티닌 (mg/dL, 숫자만)
- ast: AST/SGOT (U/L, 숫자만)
- alt: ALT/SGPT (U/L, 숫자만)
- gamma_gtp: 감마지티피/r-GTP (U/L, 숫자만)

[기타 검사]
- hepatitis_b_antigen: B형간염 항원 (텍스트, 예: "음성", "양성")
- hepatitis_b_antibody: B형간염 항체 (텍스트, 예: "음성", "양성")
- chest_xray: 흉부방사선 검사 (텍스트, 예: "정상", "이상소견 없음")

JSON 형식 예시:
{
  "height": 170.5,
  "weight": 70.0,
  "waist": 82.0,
  "bmi": 23.5,
  "vision_l": 1.0,
  "vision_r": 0.8,
  "hearing_l": "정상",
  "hearing_r": "정상",
  "bp_high": 120,
  "bp_low": 80,
  "urine_protein": "음성",
  "hemoglobin": 14.5,
  "fasting_blood_sugar": 95,
  "total_cholesterol": 180,
  "hdl_cholesterol": 55,
  "triglyceride": 120,
  "ldl_cholesterol": 110,
  "creatinine": 0.9,
  "ast": 25,
  "alt": 20,
  "gamma_gtp": 30,
  "hepatitis_b_antigen": "음성",
  "hepatitis_b_antibody": "양성",
  "chest_xray": "정상"
}

반드시 JSON 형식으로만 답해주세요. 다른 설명은 필요 없습니다.
"""
        
        try:
            response = self.model.generate_content([prompt, image])
            result_text = response.text.strip()
            
            # JSON 추출 (코드 블록으로 감싸진 경우 처리)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # JSON 파싱
            parsed_data = json.loads(result_text)
            return parsed_data
            
        except Exception as e:
            print(f"건강검진표 파싱 오류: {e}")
            return None
    
    def generate_menu_recommendations(
        self, 
        health_data: Dict[str, Any], 
        allergens: list[str], 
        menus: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        건강 정보와 메뉴 리스트를 기반으로 추천/차단 메뉴 생성
        
        Args:
            health_data: 건강 정보 딕셔너리
            allergens: 알러지 리스트
            menus: 메뉴 리스트 (각 메뉴는 id, name, ingredients, nutrition 포함)
            
        Returns:
            {
                "recommended": [메뉴 ID 리스트],
                "warnings": [{"menu_id": int, "reason": str}],
                "blocked": [{"menu_id": int, "reason": str}],
                "alternatives": [{"menu_id": int, "suggestion": str}]
            }
        """
        
        # 시스템 지시문
        system_instruction = """
너는 건강 상태와 알러지를 고려한 식이요법 전문가입니다.
사용자의 건강 정보와 알러지 정보를 바탕으로 메뉴를 평가하고 추천해주세요.

규칙:
1. 알러지 성분이 포함된 메뉴는 반드시 차단(blocked)
2. 건강 수치가 위험한 경우 해당 영양소가 많은 메뉴 경고(warnings)
   - 혈당 높음(≥100) → 당분 많은 메뉴 경고
   - LDL 높음(≥130) → 포화지방 많은 메뉴 경고
   - 중성지방 높음(≥150) → 지방 많은 메뉴 경고
   - 혈압 높음(≥130/85) → 카페인 많은 메뉴 경고
   - AST/ALT 높음 → 지방 많은 메뉴 경고
   - 헤모글로빈 낮음 → 철분 많은 음식 권장
3. 경고 메뉴에 대해 대체 옵션 제안(alternatives)
4. 안전한 메뉴는 추천(recommended)
"""
        
        # 프롬프트 생성
        prompt = f"""
사용자 건강 정보:
{json.dumps(health_data, ensure_ascii=False, indent=2)}

알러지 정보:
{json.dumps(allergens, ensure_ascii=False)}

메뉴 리스트:
{json.dumps(menus, ensure_ascii=False, indent=2)}

위 정보를 바탕으로 아래 JSON 형식으로 답해주세요:
{{
  "recommended": [추천 메뉴 ID 리스트],
  "warnings": [{{"menu_id": 메뉴ID, "reason": "경고 이유 한 줄"}}],
  "blocked": [{{"menu_id": 메뉴ID, "reason": "차단 이유 한 줄"}}],
  "alternatives": [{{"menu_id": 메뉴ID, "suggestion": "대체 옵션 제안 한 줄"}}]
}}

반드시 JSON 형식으로만 답해주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(result_text)
            return recommendations
            
        except Exception as e:
            print(f"메뉴 추천 생성 오류: {e}")
            return {
                "recommended": [],
                "warnings": [],
                "blocked": [],
                "alternatives": []
            }


# 싱글톤 인스턴스
_gemini_service_instance = None


def get_gemini_service() -> GeminiService:
    """Gemini 서비스 싱글톤 인스턴스 반환"""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance
