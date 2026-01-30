from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
import google.generativeai as genai
from dotenv import load_dotenv

# ★ DB 관련 import 추가
from app.database import get_db 
from app.models import User, UserHealth, UserAllergy 

load_dotenv()

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Gemini 설정
API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')

# [메모] 주문 기록은 아직 DB에 테이블이 없으므로 임시 저장소 유지
# (나중에 Order 테이블이 생기면 이것도 DB로 바꾸면 됩니다)
beverage_logs = {}

class BeverageItem(BaseModel):
    name: str

class OrderLog(BaseModel):
    user_id: str
    items: List[BeverageItem]

# 1. 음료 주문 로그 저장 (기존 유지)
@router.post("/log")
def log_beverage_order(order: OrderLog):
    if order.user_id not in beverage_logs:
        beverage_logs[order.user_id] = []
    
    menu_names = [item.name for item in order.items]
    beverage_logs[order.user_id].extend(menu_names)
    return {"status": "ok"}

# 2. 음료 전용 가벼운 조언 (기존 유지)
@router.get("/advice/{user_id}")
def get_beverage_advice(user_id: str):
    history = beverage_logs.get(user_id, [])
    if not history:
        return {"advice": "아직 마신 음료가 없어요. 시원한 물 한 잔 어떠세요? 💧"}
    
    recent_drinks = ", ".join(history[-3:])
    prompt = f"사용자가 최근 마신 음료: [{recent_drinks}]. 이 사람에게 해줄 짧은 건강 조언 한마디 (이모지 포함):"
    
    try:
        if model:
            response = model.generate_content(prompt)
            return {"advice": response.text}
        return {"advice": "건강을 위해 당류를 줄여보세요! 🥤"}
    except:
        return {"advice": "오늘도 건강한 하루 보내세요!"}

# ★ [핵심] 3. 종합 건강 솔루션 (여기가 진짜 DB 데이터를 씁니다!)
@router.get("/total_solution/{account_id}")
def get_total_health_solution(account_id: str, db: Session = Depends(get_db)):
    # 1) 유저 찾기 (String ID로 Integer ID 찾기)
    user = db.query(User).filter(User.account_id == account_id).first()
    
    if not user:
        return {"solution": "사용자 정보를 찾을 수 없습니다."}

    # 2) DB에서 건강검진 결과 가져오기
    health = db.query(UserHealth).filter(UserHealth.user_id == user.id).first()
    
    # 3) DB에서 알레르기 정보 가져오기
    allergy_rows = db.query(UserAllergy).filter(UserAllergy.user_id == user.id).all()
    allergies = [a.allergen_name for a in allergy_rows]

    # 4) 최근 마신 음료 (아직은 메모리에서 가져옴)
    drinks = beverage_logs.get(account_id, [])

    # 5) Gemini에게 보낼 데이터 정리
    health_info_str = "정보 없음"
    if health:
        # DB에 있는 값들 중 의미 있는 것만 뽑아서 문자열로 만듦
        info_parts = []
        if health.bmi: info_parts.append(f"BMI: {health.bmi}")
        if health.fasting_blood_sugar: info_parts.append(f"공복혈당: {health.fasting_blood_sugar}")
        if health.bp_high and health.bp_low: info_parts.append(f"혈압: {health.bp_high}/{health.bp_low}")
        if health.total_cholesterol: info_parts.append(f"콜레스테롤: {health.total_cholesterol}")
        if health.ast and health.alt: info_parts.append(f"간수치(AST/ALT): {health.ast}/{health.alt}")
        
        if info_parts:
            health_info_str = ", ".join(info_parts)

    allergy_str = ", ".join(allergies) if allergies else "없음"
    drink_str = ", ".join(drinks[-5:]) if drinks else "최근 기록 없음"

    # 6) 프롬프트 작성
    prompt = f"""
    당신은 전문 건강 컨설턴트입니다. 사용자의 실제 건강검진 데이터를 바탕으로 조언해주세요.
    
    [사용자: {user.name}]
    1. 건강검진 요약: {health_info_str}
    2. 알레르기: {allergy_str}
    3. 최근 마신 음료: {drink_str}
    
    [분석 요청]
    위의 검진 수치(혈당, 혈압, BMI 등)와 알레르기, 최근 음료 섭취 내역을 종합적으로 고려하여,
    앞으로의 식습관과 운동 방향에 대해 3줄 이내로, 전문적이지만 이해하기 쉽게 솔루션을 제공해주세요.
    """
    
    try:
        if model:
            response = model.generate_content(prompt)
            return {"solution": response.text}
        else:
            return {"solution": "AI 분석을 위한 API 키가 설정되지 않았습니다."}
    except Exception as e:
        print(f"Error: {e}")
        return {"solution": "현재 AI 서버가 혼잡하여 분석 결과를 가져올 수 없습니다."}