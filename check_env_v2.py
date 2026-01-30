from app.config import get_settings
import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 로드
load_dotenv()

print("=== Environment Variable Check ===")
try:
    settings = get_settings()
    api_key = settings.gemini_api_key
    
    if api_key:
        masked_key = api_key[:5] + "*" * (len(api_key)-5) if len(api_key) > 5 else "***"
        print(f"[INFO] Gemini API Key loaded: {masked_key}")
        
        # 실제 API 호출 테스트 (모델 리스트 조회)
        try:
            genai.configure(api_key=api_key)
            print(">> Attempting to list models with this key...")
            models = genai.list_models()
            first_model = None
            try:
                first_model = next(models)
            except StopIteration:
                pass
                
            if first_model:
                print(f"[SUCCESS] Gemini API Connection Success! Found model: {first_model.name}")
            else:
                print("[WARNING] Gemini API Connection seemed to work, but no models found.")
                
        except Exception as e:
            print(f"[FAIL] Gemini API Connection Failed: {e}")
            
    else:
        print("[FAIL] Gemini API Key is Empty or None!")
        
except Exception as e:
    print(f"[FAIL] Failed to load settings: {e}")
