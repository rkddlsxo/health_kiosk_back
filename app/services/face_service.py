"""
얼굴 인식 서비스 (InsightFace 기반)
"""
import numpy as np
from typing import Optional, List, Tuple
import cv2
from insightface.app import FaceAnalysis


class FaceService:
    """얼굴 인식 서비스 클래스"""
    
    def __init__(self):
        """InsightFace 모델 초기화"""
        self.app = FaceAnalysis(
            name='buffalo_l',  # 정확도 높은 모델
            providers=['CPUExecutionProvider']  # CPU 사용, GPU 사용시 'CUDAExecutionProvider'
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.model_name = "arcface-r100"
    
    def extract_face_embedding(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        이미지에서 얼굴 임베딩 추출
        
        Args:
            image_bytes: 이미지 바이트 데이터
            
        Returns:
            512차원 임베딩 벡터 (numpy array) 또는 None (얼굴 감지 실패 시)
        """
        # 바이트를 numpy 배열로 변환
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
        
        # 얼굴 감지 및 임베딩 추출
        faces = self.app.get(img)
        
        if len(faces) == 0:
            return None
        
        # 가장 큰 얼굴 선택 (여러 얼굴이 있을 경우)
        largest_face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        
        # 512차원 임베딩 벡터 반환
        return largest_face.embedding
    
    def embedding_to_list(self, embedding: np.ndarray) -> List[float]:
        """
        임베딩 벡터를 JSON 저장용 리스트로 변환
        
        Args:
            embedding: numpy 배열
            
        Returns:
            float 리스트
        """
        return embedding.tolist()
    
    def list_to_embedding(self, embedding_list: List[float]) -> np.ndarray:
        """
        JSON에서 가져온 리스트를 임베딩 벡터로 변환
        
        Args:
            embedding_list: float 리스트
            
        Returns:
            numpy 배열
        """
        return np.array(embedding_list, dtype=np.float32)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        두 임베딩 벡터의 코사인 유사도 계산
        
        Args:
            embedding1: 첫 번째 임베딩 벡터
            embedding2: 두 번째 임베딩 벡터
            
        Returns:
            유사도 (0~1, 높을수록 유사)
        """
        # 코사인 유사도 계산
        cos_sim = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        return float(cos_sim)
    
    def find_matching_user(
        self, 
        query_embedding: np.ndarray, 
        user_faces: List[Tuple[int, List[float]]], 
        threshold: float = 0.6
    ) -> Optional[int]:
        """
        쿼리 임베딩과 가장 유사한 사용자 찾기
        
        Args:
            query_embedding: 검색할 얼굴 임베딩
            user_faces: [(user_id, embedding_list), ...] 리스트
            threshold: 유사도 임계값 (이 값 이상이어야 매칭)
            
        Returns:
            매칭된 user_id 또는 None
        """
        best_match_id = None
        best_similarity = threshold
        
        for user_id, embedding_list in user_faces:
            user_embedding = self.list_to_embedding(embedding_list)
            similarity = self.calculate_similarity(query_embedding, user_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = user_id
        
        return best_match_id


# 싱글톤 인스턴스
_face_service_instance = None


def get_face_service() -> FaceService:
    """얼굴 인식 서비스 싱글톤 인스턴스 반환"""
    global _face_service_instance
    if _face_service_instance is None:
        _face_service_instance = FaceService()
    return _face_service_instance
