"""
대화 라우터 v2 - 노년층 특화 대화 처리
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversation"])

# 간단한 세션 저장소 (실제로는 Redis 사용)
active_sessions: Dict[str, Dict[str, Any]] = {}


class UserProfile(BaseModel):
    name: str = Field(..., description="사용자 이름")
    age: int = Field(..., ge=65, le=120, description="나이")
    gender: str = Field(..., description="성별")
    birth_place: Optional[str] = Field(None, description="출생지")
    occupation: Optional[str] = Field(None, description="직업")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    message: str = Field(..., max_length=2000, description="사용자 메시지")
    message_type: str = Field(default="text", description="메시지 유형")
    user_context: Optional[UserProfile] = Field(None, description="사용자 컨텍스트")
    conversation_settings: Optional[Dict[str, Any]] = Field(None, description="대화 설정")


class ContextUpdateRequest(BaseModel):
    user_profile_updates: Optional[Dict[str, Any]] = Field(None, description="사용자 프로필 업데이트")
    conversation_history_summary: Optional[str] = Field(None, description="대화 히스토리 요약")


@router.get("/health")
async def health_check():
    """대화 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "conversation_processing",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "features": [
            "elderly_optimized_chat",
            "chapter_classification",
            "context_awareness"
        ],
        "ai_models": {
            "primary": "claude-3-sonnet-20240229",
            "fallback": "claude-3-haiku-20240307",
            "status": "available"
        }
    }


@router.post("/chat")
async def process_chat(request: ChatRequest):
    """실시간 대화 처리"""
    try:
        # 세션 확인 또는 생성
        if request.session_id not in active_sessions:
            active_sessions[request.session_id] = {
                "created_at": datetime.utcnow(),
                "message_count": 0,
                "user_context": request.user_context.dict() if request.user_context else {},
                "conversation_history": []
            }
        
        session = active_sessions[request.session_id]
        session["message_count"] += 1
        session["last_activity"] = datetime.utcnow()
        
        # 노년층 특화 응답 생성 (실제로는 Claude 3 사용)
        ai_response = generate_elderly_friendly_response(request.message, session)
        
        # 간단한 챕터 분류 (키워드 기반)
        chapter_classification = classify_message_simple(request.message)
        
        # 기억 중요도 평가
        memory_classification = evaluate_memory_importance(request.message)
        
        # 후속 질문 생성
        suggested_questions = generate_follow_up_questions(request.message)
        
        # 대화 히스토리에 추가
        session["conversation_history"].append({
            "user_message": request.message,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow(),
            "chapter_classification": chapter_classification
        })
        
        return {
            "success": True,
            "session_id": request.session_id,
            "ai_response": ai_response,
            "processing_time": 2.5,
            "analysis_results": {
                "chapter_classification": chapter_classification,
                "memory_classification": memory_classification
            },
            "suggested_questions": suggested_questions,
            "conversation_context": {
                "topic_continuity": extract_topic(request.message),
                "suggested_next_topics": generate_next_topics(request.message)
            }
        }
        
    except Exception as e:
        logger.error(f"대화 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"대화 처리 중 오류가 발생했습니다: {str(e)}")


@router.put("/context/{session_id}")
async def update_context(session_id: str, request: ContextUpdateRequest):
    """대화 컨텍스트 업데이트"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
        
        session = active_sessions[session_id]
        
        # 사용자 프로필 업데이트
        if request.user_profile_updates:
            session["user_context"].update(request.user_profile_updates)
        
        # 대화 히스토리 요약 업데이트
        if request.conversation_history_summary:
            session["history_summary"] = request.conversation_history_summary
        
        session["last_updated"] = datetime.utcnow()
        
        return {
            "success": True,
            "context_updated": True,
            "session_id": session_id,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"컨텍스트 업데이트 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"컨텍스트 업데이트 중 오류가 발생했습니다: {str(e)}")


@router.get("/sessions")
async def get_active_sessions():
    """활성 세션 목록 조회"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }


# 헬퍼 함수들
def generate_elderly_friendly_response(message: str, session: Dict[str, Any]) -> str:
    """노년층 친화적 응답 생성"""
    # 실제로는 Claude 3를 사용하지만, 여기서는 간단한 응답 생성
    user_name = session.get("user_context", {}).get("name", "어르신")
    
    if "어린 시절" in message or "어렸을 때" in message:
        return f"{user_name}님의 어린 시절 이야기가 정말 소중하게 느껴집니다. 그때 가장 기억에 남는 순간은 어떤 것이었나요?"
    elif "가족" in message or "부모" in message:
        return f"가족에 대한 따뜻한 마음이 전해집니다. {user_name}님께서 가족과 함께한 특별한 순간이 있으시다면 들려주세요."
    elif "전쟁" in message or "피난" in message:
        return f"그 어려운 시절을 겪으셨군요. {user_name}님의 경험이 정말 소중한 역사의 증언입니다. 그때 기분은 어떠셨나요?"
    else:
        return f"{user_name}님의 소중한 이야기를 들려주셔서 감사합니다. 더 자세히 말씀해 주실 수 있나요?"


def classify_message_simple(message: str) -> Dict[str, Any]:
    """간단한 키워드 기반 챕터 분류"""
    keywords_map = {
        "growth_childhood": ["어린 시절", "어렸을 때", "유년기", "아이", "어린"],
        "family_parents": ["부모", "아버지", "어머니", "아빠", "엄마"],
        "school_friends": ["친구", "학교", "대학", "동창"],
        "society_country": ["전쟁", "피난", "나라", "국가"],
        "career_experience": ["직업", "일", "회사", "직장"]
    }
    
    for chapter, keywords in keywords_map.items():
        if any(keyword in message for keyword in keywords):
            return {
                "primary_chapter": chapter,
                "confidence": 0.85,
                "alternative_chapters": []
            }
    
    return {
        "primary_chapter": "others_general",
        "confidence": 0.5,
        "alternative_chapters": []
    }


def evaluate_memory_importance(message: str) -> Dict[str, Any]:
    """기억 중요도 평가"""
    importance_keywords = ["처음", "가장", "특별한", "잊을 수 없는", "인상 깊은"]
    importance_score = 0.5
    
    for keyword in importance_keywords:
        if keyword in message:
            importance_score += 0.1
    
    return {
        "memory_type": "personal_experience",
        "importance_score": min(importance_score, 1.0),
        "life_stage": "elderly",
        "autobiography_relevance": "high" if importance_score > 0.7 else "medium"
    }


def generate_follow_up_questions(message: str) -> List[str]:
    """후속 질문 생성"""
    base_questions = [
        "그때 가장 기억에 남는 일은 무엇인가요?",
        "그 경험에서 배운 점이 있다면 무엇인가요?",
        "비슷한 다른 경험도 있으신가요?"
    ]
    
    if "가족" in message:
        return [
            "가족과 함께한 가장 행복했던 순간은 언제인가요?",
            "가족에게서 배운 가장 소중한 가르침은 무엇인가요?",
            "후손들에게 전하고 싶은 가족의 이야기가 있나요?"
        ]
    elif "어린 시절" in message:
        return [
            "어린 시절 가장 좋아했던 놀이는 무엇이었나요?",
            "그때 꿈꾸던 것이 있으시다면 무엇이었나요?",
            "어린 시절의 친구들과는 지금도 연락하시나요?"
        ]
    
    return base_questions


def extract_topic(message: str) -> str:
    """메시지에서 주제 추출"""
    if "가족" in message:
        return "family_relationships"
    elif "어린 시절" in message:
        return "childhood_memories"
    elif "전쟁" in message:
        return "war_experience"
    else:
        return "general_life_story"


def generate_next_topics(message: str) -> List[str]:
    """다음 주제 제안"""
    if "가족" in message:
        return ["childhood_with_family", "family_traditions", "parenting_experience"]
    elif "어린 시절" in message:
        return ["school_memories", "childhood_friends", "family_during_childhood"]
    else:
        return ["family_relationships", "career_life", "life_wisdom"]
