"""
Vector Database Service - 개인화된 질문 생성을 위한 벡터 검색
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorService:
    """Vector Database를 사용한 개인화 서비스"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Chroma 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 컬렉션 생성/가져오기
        self.conversations_collection = self._get_or_create_collection(
            "conversations", 
            "사용자 대화 내용 저장"
        )
        
        self.questions_collection = self._get_or_create_collection(
            "questions",
            "효과적인 질문 패턴 저장"
        )
        
        # 초기 데이터 로드
        self._initialize_sample_data()
        
        logger.info(f"Vector Database 초기화 완료: {persist_directory}")
    
    def _get_or_create_collection(self, name: str, description: str):
        """컬렉션 생성 또는 가져오기"""
        try:
            return self.client.get_collection(name=name)
        except Exception:
            return self.client.create_collection(
                name=name,
                metadata={"description": description}
            )
    
    def _initialize_sample_data(self):
        """샘플 데이터 초기화"""
        # 기존 데이터 확인
        if self.questions_collection.count() > 0:
            logger.info("기존 질문 데이터가 존재합니다.")
            return
        
        # 노년층 맞춤 질문 패턴 데이터
        sample_questions = [
            {
                "id": "childhood_home",
                "question": "어린 시절 살던 집은 어떤 모습이었나요?",
                "category": "childhood",
                "effectiveness": 0.9,
                "context": "집, 거주지, 어린시절"
            },
            {
                "id": "family_memories",
                "question": "가족들과 함께 했던 가장 특별한 추억이 있으시다면?",
                "category": "family",
                "effectiveness": 0.95,
                "context": "가족, 추억, 특별한 순간"
            },
            {
                "id": "mother_cooking",
                "question": "어머니께서 해주신 음식 중 가장 그리운 것은 무엇인가요?",
                "category": "food",
                "effectiveness": 0.92,
                "context": "음식, 어머니, 요리, 그리움"
            },
            {
                "id": "childhood_friends",
                "question": "어린 시절 친구들과 어떤 놀이를 하며 시간을 보내셨나요?",
                "category": "friendship",
                "effectiveness": 0.88,
                "context": "친구, 놀이, 어린시절, 게임"
            },
            {
                "id": "school_memories",
                "question": "학창시절 가장 기억에 남는 선생님이나 친구가 있으신가요?",
                "category": "education",
                "effectiveness": 0.87,
                "context": "학교, 선생님, 친구, 교육"
            },
            {
                "id": "first_job",
                "question": "처음 직장을 구했을 때의 기분이나 경험을 들려주세요",
                "category": "career",
                "effectiveness": 0.85,
                "context": "직장, 일, 첫 경험, 사회생활"
            },
            {
                "id": "marriage_story",
                "question": "배우자를 처음 만났을 때의 이야기를 들려주실 수 있나요?",
                "category": "love",
                "effectiveness": 0.93,
                "context": "결혼, 배우자, 사랑, 만남"
            },
            {
                "id": "children_birth",
                "question": "자녀가 태어났을 때의 감정을 기억하고 계신가요?",
                "category": "parenting",
                "effectiveness": 0.94,
                "context": "자녀, 출산, 부모, 감정"
            },
            {
                "id": "hometown_changes",
                "question": "고향이 예전과 비교해서 어떻게 변했나요?",
                "category": "hometown",
                "effectiveness": 0.86,
                "context": "고향, 변화, 과거와 현재"
            },
            {
                "id": "grandchildren_joy",
                "question": "손자손녀와 함께하는 시간 중 가장 행복한 순간은?",
                "category": "grandparenting",
                "effectiveness": 0.96,
                "context": "손자, 손녀, 행복, 가족"
            }
        ]
        
        # 벡터화 및 저장
        questions = [item["question"] for item in sample_questions]
        embeddings = self.model.encode(questions).tolist()
        
        self.questions_collection.add(
            embeddings=embeddings,
            documents=questions,
            metadatas=[{
                "category": item["category"],
                "effectiveness": item["effectiveness"],
                "context": item["context"]
            } for item in sample_questions],
            ids=[item["id"] for item in sample_questions]
        )
        
        logger.info(f"샘플 질문 {len(sample_questions)}개 저장 완료")
    
    def store_conversation(self, session_id: str, user_message: str, ai_response: str, 
                          user_profile: Dict[str, Any]) -> None:
        """사용자 대화 저장"""
        try:
            # 대화 내용 벡터화
            conversation_text = f"사용자: {user_message}\nAI: {ai_response}"
            embedding = self.model.encode([conversation_text])[0].tolist()
            
            # 메타데이터 구성
            metadata = {
                "session_id": session_id,
                "user_name": user_profile.get("name", ""),
                "user_age": user_profile.get("age", 0),
                "user_interests": ",".join(user_profile.get("interests", [])),
                "timestamp": datetime.now().isoformat(),
                "message_length": len(user_message)
            }
            
            # 저장
            doc_id = f"{session_id}_{datetime.now().timestamp()}"
            self.conversations_collection.add(
                embeddings=[embedding],
                documents=[conversation_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"대화 저장 완료: {session_id}")
            
        except Exception as e:
            logger.error(f"대화 저장 실패: {e}")
    
    def get_personalized_questions(self, user_message: str, user_profile: Dict[str, Any], 
                                 limit: int = 3) -> List[Dict[str, Any]]:
        """개인화된 후속 질문 생성"""
        try:
            # 사용자 메시지 벡터화
            query_embedding = self.model.encode([user_message])[0].tolist()
            
            # 유사한 질문 검색
            results = self.questions_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # 더 많이 가져와서 필터링
                include=["documents", "metadatas", "distances"]
            )
            
            # 사용자 관심사와 매칭
            user_interests = user_profile.get("interests", [])
            personalized_questions = []
            
            for i, (question, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0], 
                results["distances"][0]
            )):
                # 관심사 매칭 점수 계산
                interest_score = self._calculate_interest_score(metadata["context"], user_interests)
                
                # 최종 점수 (유사도 + 관심사 + 효과성)
                final_score = (
                    (1 - distance) * 0.4 +  # 유사도 (거리가 작을수록 좋음)
                    interest_score * 0.3 +   # 관심사 매칭
                    metadata["effectiveness"] * 0.3  # 질문 효과성
                )
                
                personalized_questions.append({
                    "question": question,
                    "category": metadata["category"],
                    "score": final_score,
                    "similarity": 1 - distance,
                    "interest_match": interest_score,
                    "effectiveness": metadata["effectiveness"]
                })
            
            # 점수순 정렬 후 상위 N개 반환
            personalized_questions.sort(key=lambda x: x["score"], reverse=True)
            
            return personalized_questions[:limit]
            
        except Exception as e:
            logger.error(f"개인화 질문 생성 실패: {e}")
            return self._get_fallback_questions(limit)
    
    def _calculate_interest_score(self, context: str, user_interests: List[str]) -> float:
        """사용자 관심사와 질문 컨텍스트 매칭 점수"""
        if not user_interests:
            return 0.5  # 기본 점수
        
        context_lower = context.lower()
        matches = 0
        
        for interest in user_interests:
            if interest.lower() in context_lower:
                matches += 1
        
        return min(matches / len(user_interests) + 0.3, 1.0)
    
    def _get_fallback_questions(self, limit: int) -> List[Dict[str, Any]]:
        """기본 질문 (벡터 검색 실패 시)"""
        fallback = [
            {
                "question": "어린 시절 가장 행복했던 순간을 들려주세요",
                "category": "childhood",
                "score": 0.8,
                "similarity": 0.7,
                "interest_match": 0.5,
                "effectiveness": 0.9
            },
            {
                "question": "가족과 함께한 특별한 추억이 있으시다면?",
                "category": "family", 
                "score": 0.75,
                "similarity": 0.7,
                "interest_match": 0.5,
                "effectiveness": 0.85
            },
            {
                "question": "지금까지 살아오면서 가장 자랑스러운 일은 무엇인가요?",
                "category": "achievement",
                "score": 0.7,
                "similarity": 0.6,
                "interest_match": 0.5,
                "effectiveness": 0.9
            }
        ]
        
        return fallback[:limit]
    
    def find_similar_experiences(self, user_message: str, limit: int = 3) -> List[Dict[str, Any]]:
        """유사한 경험을 가진 다른 사용자 대화 검색"""
        try:
            if self.conversations_collection.count() == 0:
                return []
            
            # 사용자 메시지 벡터화
            query_embedding = self.model.encode([user_message])[0].tolist()
            
            # 유사한 대화 검색
            results = self.conversations_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            similar_experiences = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similar_experiences.append({
                    "conversation": doc,
                    "user_name": metadata.get("user_name", "익명"),
                    "similarity": 1 - distance,
                    "timestamp": metadata.get("timestamp", "")
                })
            
            return similar_experiences
            
        except Exception as e:
            logger.error(f"유사 경험 검색 실패: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Vector Database 통계"""
        try:
            return {
                "conversations_count": self.conversations_collection.count(),
                "questions_count": self.questions_collection.count(),
                "model_name": self.model.get_sentence_embedding_dimension(),
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {
                "conversations_count": 0,
                "questions_count": 0,
                "error": str(e)
            }

# 전역 인스턴스
vector_service = None

def get_vector_service() -> VectorService:
    """Vector Service 싱글톤 인스턴스 반환"""
    global vector_service
    if vector_service is None:
        vector_service = VectorService()
    return vector_service
