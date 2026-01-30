"""
인증 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models import User, UserFace
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.services.face_service import get_face_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    # bcrypt는 72바이트 제한이 있으므로 UTF-8 인코딩 후 확인
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes.decode('utf-8'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=UserResponse)
async def register_user(
    account_id: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    사용자 회원가입 (얼굴 이미지 포함)
    """
    # 계정 ID 중복 확인
    existing_user = db.query(User).filter(User.account_id == account_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 계정 ID입니다")
    
    # 얼굴 임베딩 추출
    face_service = get_face_service()
    image_bytes = await face_image.read()
    embedding = face_service.extract_face_embedding(image_bytes)
    
    if embedding is None:
        raise HTTPException(status_code=400, detail="얼굴을 감지할 수 없습니다")
    
    # 사용자 생성
    hashed_pw = hash_password(password)
    new_user = User(
        account_id=account_id,
        password=hashed_pw,
        name=name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # UserFace 생성
    embedding_list = face_service.embedding_to_list(embedding)
    user_face = UserFace(
        user_id=new_user.id,
        embedding=embedding_list,
        embedding_model=face_service.model_name
    )
    db.add(user_face)
    db.commit()
    
    return new_user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    계정 ID + 비밀번호로 로그인
    """
    user = db.query(User).filter(User.account_id == login_data.account_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="계정 정보가 올바르지 않습니다")
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="계정 정보가 올바르지 않습니다")
    
    return LoginResponse(
        success=True,
        message="로그인 성공",
        user_id=user.id,
        user_name=user.name
    )


@router.post("/login/face", response_model=LoginResponse)
async def face_login(
    face_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    얼굴 인식으로 로그인
    """
    face_service = get_face_service()
    
    # 입력 얼굴 임베딩 추출
    image_bytes = await face_image.read()
    query_embedding = face_service.extract_face_embedding(image_bytes)
    
    if query_embedding is None:
        raise HTTPException(status_code=400, detail="얼굴을 감지할 수 없습니다")
    
    # 모든 사용자 얼굴 가져오기
    user_faces = db.query(UserFace).all()
    
    if not user_faces:
        raise HTTPException(status_code=404, detail="등록된 사용자가 없습니다")
    
    # 유사도 비교
    user_face_data = [(uf.user_id, uf.embedding) for uf in user_faces]
    
    from app.config import get_settings
    settings = get_settings()
    
    matched_user_id = face_service.find_matching_user(
        query_embedding,
        user_face_data,
        threshold=settings.face_similarity_threshold
    )
    
    if matched_user_id is None:
        raise HTTPException(status_code=401, detail=" 일치하는 사용자를 찾을 수 없습니다")
    
    # 사용자 정보 조회
    user = db.query(User).filter(User.id == matched_user_id).first()
    
    return LoginResponse(
        success=True,
        message="얼굴 인식 로그인 성공",
        user_id=user.id,
        user_name=user.name
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 정보 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    return user
