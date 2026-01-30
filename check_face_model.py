import os
import sys

# 현재 디렉토리를 path에 추가하여 app 모듈 import 가능하게 함
sys.path.append(os.getcwd())

print(">> FaceService 로딩 시도...")

try:
    from app.services.face_service import get_face_service
    
    print(">> get_face_service() 호출...")
    service = get_face_service()
    
    print(">> 모델 로딩 완료 여부 확인...")
    if service.app:
        print("✅ FaceAnalysis app loaded successfully.")
    else:
        print("❌ FaceAnalysis app is None.")
        
    print(">> Dummy 이미지로 테스트...")
    import numpy as np
    import cv2
    
    # 640x640 검은 이미지 생성
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    embedding = service.extract_face_embedding(cv2.imencode('.jpg', dummy_img)[1].tobytes())
    
    print(f"✅ Embedding extraction ran without crashing. Result: {type(embedding)}")
    
except Exception as e:
    print(f"❌ Failed to load FaceService: {e}")
    import traceback
    traceback.print_exc()
