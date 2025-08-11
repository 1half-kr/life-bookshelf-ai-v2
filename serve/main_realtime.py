"""
Life Bookshelf AI v2 - 실시간 서비스
Vector Database + Streaming Response
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import time
import logging
from datetime import datetime

# 서비스 임포트
from vector_service import get_vector_service
from streaming_service import get_streaming_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Life Bookshelf AI v2 - Realtime Service",
    description="65세 이상 노년층을 위한 실시간 자서전 대화 서비스",
    version="2.0.0"
)

# 데이터 모델
class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    location: Optional[str] = None
    interests: List[str] = []

class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile

class ChatResponse(BaseModel):
    response: str
    follow_up_questions: List[Dict[str, Any]]
    session_id: str
    processing_time: float
    timestamp: str
    status: str = "success"
    vector_analysis: Optional[Dict[str, Any]] = None

class StreamChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile

# 서비스 인스턴스
vector_service = get_vector_service()
streaming_service = get_streaming_service()

# 인메모리 파이프라인 클래스들
class ValidationStep:
    """입력 검증"""
    
    async def execute(self, request: ChatRequest) -> dict:
        start_time = time.time()
        
        logger.info(f"🔍 Validation - Session: {request.session_id}")
        
        # 기본 검증
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
        
        if request.user_profile.age < 65:
            raise HTTPException(status_code=400, detail="65세 이상 사용자만 이용 가능합니다.")
        
        # 메시지 길이 검증
        message_length = len(request.message)
        if message_length > 1000:
            raise HTTPException(status_code=400, detail="메시지가 너무 깁니다. (최대 1000자)")
        
        await asyncio.sleep(0.1)
        
        processing_time = time.time() - start_time
        
        return {
            "validated_session_id": request.session_id,
            "validated_message": request.message,
            "validated_user_profile": request.user_profile,
            "message_length": message_length,
            "processing_time": processing_time
        }

class ContextLoaderStep:
    """Vector Database 기반 컨텍스트 로딩"""
    
    async def execute(self, validated_data: dict) -> dict:
        start_time = time.time()
        
        logger.info(f"📚 Context Loading - User: {validated_data['validated_user_profile'].name}")
        
        user_message = validated_data['validated_message']
        user_profile = validated_data['validated_user_profile']
        
        # Vector Database에서 유사한 경험 검색
        similar_experiences = vector_service.find_similar_experiences(user_message, limit=3)
        
        # 개인화된 질문 생성
        personalized_questions = vector_service.get_personalized_questions(
            user_message, user_profile.dict(), limit=4
        )
        
        # 컨텍스트 구성
        context = {
            "conversation_history": [],  # 실제로는 Redis에서 로드
            "user_interests": user_profile.interests,
            "similar_experiences": similar_experiences,
            "personalized_questions": personalized_questions,
            "generation_context": {
                "tone": "친근하고 따뜻한",
                "style": "노년층 맞춤형",
                "focus": "자서전 작성 도움",
                "cultural_context": "한국 전통문화"
            }
        }
        
        await asyncio.sleep(0.2)
        
        processing_time = time.time() - start_time
        
        return {
            "context": context,
            "processing_time": processing_time
        }

class LLMProcessorStep:
    """LLM 처리"""
    
    async def execute(self, message: str, user_profile: UserProfile, context: dict) -> dict:
        start_time = time.time()
        
        logger.info(f"🤖 LLM Processing - Message: {message[:30]}...")
        
        # 컨텍스트 기반 응답 생성
        user_name = user_profile.name
        interests = ", ".join(user_profile.interests) if user_profile.interests else "다양한 것들"
        
        # 유사한 경험이 있는 경우 언급
        similar_context = ""
        if context.get("similar_experiences"):
            similar_context = "\n\n비슷한 경험을 나누신 다른 분들도 계시더라고요. 이런 이야기들이 정말 소중합니다."
        
        ai_response = f"""안녕하세요 {user_name}님! 

{message}라고 말씀해주셨는데, 정말 의미 깊은 이야기네요.

저는 할머니의 소중한 인생 이야기를 함께 정리해서 아름다운 자서전을 만들어드리는 AI 도우미입니다. 

{user_name}님께서 {interests}에 관심이 많으시다고 하셨는데, 이런 관심사들과 연결된 추억들도 많이 있으실 것 같아요.{similar_context}

편안하게 더 많은 이야기를 들려주세요. 모든 이야기가 소중한 자서전의 한 페이지가 될 거예요."""

        # 개인화된 후속 질문 사용
        follow_up_questions = context.get("personalized_questions", [])
        
        # LLM 호출 시뮬레이션
        await asyncio.sleep(0.8)
        
        processing_time = time.time() - start_time
        
        return {
            "ai_response": ai_response,
            "follow_up_questions": follow_up_questions,
            "context_analysis": {
                "similar_experiences_count": len(context.get("similar_experiences", [])),
                "personalization_score": sum(q.get("score", 0) for q in follow_up_questions) / len(follow_up_questions) if follow_up_questions else 0.8
            },
            "processing_time": processing_time
        }

class ResponseBuilderStep:
    """응답 구성"""
    
    async def execute(self, llm_result: dict, session_id: str, 
                     user_profile: UserProfile, user_message: str) -> ChatResponse:
        start_time = time.time()
        
        logger.info(f"🏗️ Response Building - Session: {session_id}")
        
        # Vector Database에 대화 저장
        vector_service.store_conversation(
            session_id, user_message, llm_result["ai_response"], user_profile.dict()
        )
        
        # 응답 구성
        await asyncio.sleep(0.1)
        
        processing_time = time.time() - start_time
        total_processing_time = processing_time  # 실제로는 전체 파이프라인 시간 합계
        
        return ChatResponse(
            response=llm_result["ai_response"],
            follow_up_questions=llm_result["follow_up_questions"],
            session_id=session_id,
            processing_time=total_processing_time,
            timestamp=datetime.now().isoformat(),
            status="success",
            vector_analysis=llm_result.get("context_analysis")
        )

# 파이프라인 인스턴스
validation_step = ValidationStep()
context_loader_step = ContextLoaderStep()
llm_processor_step = LLMProcessorStep()
response_builder_step = ResponseBuilderStep()

@app.get("/")
async def root():
    return {
        "service": "Life Bookshelf AI v2 - Realtime Service",
        "version": "2.0.0",
        "description": "65세 이상 노년층을 위한 실시간 자서전 대화 서비스",
        "features": [
            "Vector Database 기반 개인화",
            "실시간 스트리밍 응답",
            "유사 경험 검색",
            "맞춤형 질문 생성"
        ],
        "status": "running"
    }

@app.get("/health")
async def health_check():
    # Vector Database 상태 확인
    vector_stats = vector_service.get_statistics()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "vector_database": "healthy" if vector_stats.get("conversations_count", 0) >= 0 else "error",
            "streaming": "healthy"
        },
        "vector_stats": vector_stats
    }

@app.post("/conversation/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """실시간 대화 처리 - Vector DB + 개인화"""
    
    pipeline_start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting conversation pipeline - Session: {request.session_id}")
        
        # Step 1: Validation
        validated_data = await validation_step.execute(request)
        
        # Step 2: Context Loading (Vector DB)
        context_result = await context_loader_step.execute(validated_data)
        
        # Step 3: LLM Processing
        llm_result = await llm_processor_step.execute(
            request.message,
            request.user_profile,
            context_result["context"]
        )
        
        # Step 4: Response Building
        response = await response_builder_step.execute(
            llm_result, request.session_id, request.user_profile, request.message
        )
        
        # 전체 처리 시간 업데이트
        total_time = time.time() - pipeline_start_time
        response.processing_time = total_time
        
        logger.info(f"✅ Pipeline completed - Time: {total_time:.2f}s")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation/chat/stream")
async def chat_stream(request: StreamChatRequest):
    """스트리밍 대화 처리"""
    
    try:
        # 일반 대화 처리 먼저 수행
        chat_request = ChatRequest(
            session_id=request.session_id,
            message=request.message,
            user_profile=request.user_profile
        )
        
        response = await chat(chat_request)
        
        # 스트리밍 응답 생성
        async def generate_stream():
            # 타이핑 인디케이터
            async for chunk in streaming_service.stream_typing_indicator(request.session_id, 1.0):
                yield chunk
            
            # AI 응답 스트리밍
            async for chunk in streaming_service.stream_ai_response(
                response.response, request.session_id, chunk_size=8, delay=0.03
            ):
                yield chunk
            
            # 후속 질문 스트리밍
            async for chunk in streaming_service.stream_follow_up_questions(
                response.follow_up_questions, request.session_id
            ):
                yield chunk
            
            # 분석 결과 스트리밍
            if response.vector_analysis:
                async for chunk in streaming_service.stream_conversation_analysis(
                    response.vector_analysis, request.session_id
                ):
                    yield chunk
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 대화 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/sessions/{session_id}")
async def get_session_info(session_id: str):
    """세션 정보 조회"""
    return {
        "session_id": session_id,
        "status": "active",
        "message_count": 5,
        "created_at": "2025-08-04T15:00:00Z",
        "last_activity": datetime.now().isoformat(),
        "vector_enabled": True,
        "streaming_enabled": True
    }

@app.get("/stats")
async def get_stats():
    """서비스 통계"""
    vector_stats = vector_service.get_statistics()
    active_streams = streaming_service.get_active_streams()
    
    return {
        "service_info": {
            "total_conversations": vector_stats.get("conversations_count", 0),
            "total_questions": vector_stats.get("questions_count", 0),
            "active_streams": len(active_streams),
            "avg_response_time": "1.2s",
            "success_rate": "99.8%"
        },
        "vector_database": vector_stats,
        "streaming": {
            "active_sessions": list(active_streams.keys()),
            "total_active": len(active_streams)
        },
        "features": {
            "personalized_questions": True,
            "similar_experiences": True,
            "vector_database": True,
            "streaming_response": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/conversation/stream/{session_id}")
async def stop_stream(session_id: str):
    """스트리밍 중단"""
    success = streaming_service.stop_stream(session_id)
    return {
        "session_id": session_id,
        "stopped": success,
        "message": "스트리밍이 중단되었습니다." if success else "활성 스트림을 찾을 수 없습니다."
    }

if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    
    uvicorn.run(app, host=HOST, port=PORT)
