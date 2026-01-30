"""
키오스크 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserFace
from app.services.face_service import get_face_service
import json

router = APIRouter(prefix="/api/kiosk", tags=["kiosk"])


@router.post("/detect-face")
async def detect_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    얼굴 인식으로 사용자 확인 (키오스크용)
    """
    face_service = get_face_service()
    
    # 입력 얼굴 임베딩 추출
    image_bytes = await file.read()
    query_embedding = face_service.extract_face_embedding(image_bytes)
    
    if query_embedding is None:
        return {
            "match": False,
            "message": "얼굴을 감지할 수 없습니다"
        }
    
    # 모든 사용자 얼굴 가져오기
    user_faces = db.query(UserFace).all()
    
    if not user_faces:
        return {
            "match": False,
            "message": "등록된 사용자가 없습니다"
        }
    
    # 유사도 비교
    user_face_data = []
    for uf in user_faces:
        try:
            embedding_list = json.loads(uf.embedding)
            user_face_data.append((uf.user_id, embedding_list))
        except Exception:
            continue
    
    from app.config import get_settings
    settings = get_settings()
    
    matched_user_id = face_service.find_matching_user(
        query_embedding,
        user_face_data,
        threshold=settings.face_similarity_threshold
    )
    
    if matched_user_id is None:
        return {
            "match": False,
            "message": "일치하는 사용자를 찾을 수 없습니다"
        }
    
    # 사용자 정보 조회
    user = db.query(User).filter(User.id == matched_user_id).first()
    
    return {
        "match": True,
        "message": "얼굴 인식 성공",
        "user_id": user.id,
        "name": user.name,
        "account_id": user.account_id
    }
