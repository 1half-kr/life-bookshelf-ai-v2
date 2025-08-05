"""
Life Bookshelf AI v2 - 간단한 실시간 서비스 (Vector DB 없이)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import time
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Life Bookshelf AI v2 - Simple Service",
    description="65세 이상 노년층을 위한 간단한 자서전 대화 서비스",
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
    follow_up_questions: List[str]
    session_id: str
    processing_time: float
    timestamp: str
    status: str = "success"

class StreamChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: UserProfile

# 간단한 스트리밍 서비스
class SimpleStreamingService:
    def __init__(self):
        self.active_streams = {}
    
    async def stream_ai_response(self, response_text: str, session_id: str, 
                               chunk_size: int = 8, delay: float = 0.05):
        """AI 응답을 실시간으로 스트리밍"""
        try:
            self.active_streams[session_id] = True
            
            # 시작 이벤트
            yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
            
            # 텍스트를 청크 단위로 분할하여 스트리밍
            words = response_text.split()
            current_chunk = ""
            
            for i, word in enumerate(words):
                if session_id not in self.active_streams:
                    break
                
                current_chunk += word + " "
                
                # 청크 크기에 도달하거나 마지막 단어인 경우
                if (i + 1) % chunk_size == 0 or i == len(words) - 1:
                    chunk_data = {
                        "type": "chunk",
                        "content": current_chunk.strip(),
                        "progress": (i + 1) / len(words),
                        "session_id": session_id
                    }
                    
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    current_chunk = ""
                    
                    # 자연스러운 타이핑 효과를 위한 지연
                    await asyncio.sleep(delay)
            
            # 완료 이벤트
            completion_data = {
                "type": "complete",
                "session_id": session_id,
                "total_words": len(words),
                "timestamp": datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            # 스트림 정리
            if session_id in self.active_streams:
                del self.active_streams[session_id]
                
        except Exception as e:
            logger.error(f"스트리밍 오류: {e}")
            error_data = {
                "type": "error",
                "message": str(e),
                "session_id": session_id
            }
            yield f"data: {json.dumps(error_data)}\n\n"

# 서비스 인스턴스
streaming_service = SimpleStreamingService()

# 기본 질문 데이터
DEFAULT_QUESTIONS = [
    "어린 시절 살던 집은 어떤 모습이었나요?",
    "가족들과 함께 했던 가장 특별한 추억이 있으시다면?",
    "어머니께서 해주신 음식 중 가장 그리운 것은 무엇인가요?",
    "어린 시절 친구들과 어떤 놀이를 하며 시간을 보내셨나요?",
    "학창시절 가장 기억에 남는 선생님이나 친구가 있으신가요?"
]

@app.get("/")
async def root():
    return {
        "service": "Life Bookshelf AI v2 - Simple Service",
        "version": "2.0.0",
        "description": "65세 이상 노년층을 위한 간단한 자서전 대화 서비스",
        "features": [
            "실시간 스트리밍 응답",
            "기본 질문 생성",
            "노년층 맞춤 대화"
        ],
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "streaming": "healthy",
            "basic_chat": "healthy"
        }
    }

@app.post("/conversation/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """간단한 대화 처리"""
    
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Chat request - Session: {request.session_id}")
        
        # 기본 검증
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
        
        if request.user_profile.age < 65:
            raise HTTPException(status_code=400, detail="65세 이상 사용자만 이용 가능합니다.")
        
        # 간단한 AI 응답 생성
        user_name = request.user_profile.name
        interests = ", ".join(request.user_profile.interests) if request.user_profile.interests else "다양한 것들"
        
        ai_response = f"""안녕하세요 {user_name}님! 

"{request.message}"라고 말씀해주셨는데, 정말 의미 깊은 이야기네요.

저는 할머니의 소중한 인생 이야기를 함께 정리해서 아름다운 자서전을 만들어드리는 AI 도우미입니다. 

{user_name}님께서 {interests}에 관심이 많으시다고 하셨는데, 이런 관심사들과 연결된 추억들도 많이 있으실 것 같아요.

편안하게 더 많은 이야기를 들려주세요. 모든 이야기가 소중한 자서전의 한 페이지가 될 거예요."""

        # 기본 후속 질문 (랜덤하게 3개 선택)
        import random
        follow_up_questions = random.sample(DEFAULT_QUESTIONS, 3)
        
        # 처리 시간 계산
        processing_time = time.time() - start_time
        
        response = ChatResponse(
            response=ai_response,
            follow_up_questions=follow_up_questions,
            session_id=request.session_id,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
        
        logger.info(f"✅ Chat completed - Time: {processing_time:.2f}s")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
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
            # AI 응답 스트리밍
            async for chunk in streaming_service.stream_ai_response(
                response.response, request.session_id, chunk_size=6, delay=0.04
            ):
                yield chunk
            
            # 후속 질문들 스트리밍
            await asyncio.sleep(0.5)
            for i, question in enumerate(response.follow_up_questions):
                question_event = {
                    "type": "follow_up_question",
                    "question": question,
                    "index": i + 1,
                    "total": len(response.follow_up_questions),
                    "session_id": request.session_id
                }
                
                yield f"data: {json.dumps(question_event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.3)
        
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
        "message_count": 1,
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "streaming_enabled": True
    }

@app.get("/stats")
async def get_stats():
    """서비스 통계"""
    return {
        "service_info": {
            "total_conversations": 0,
            "active_streams": len(streaming_service.active_streams),
            "avg_response_time": "0.5s",
            "success_rate": "100%"
        },
        "features": {
            "basic_chat": True,
            "streaming_response": True,
            "simple_questions": True
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Life Bookshelf AI v2 - Simple Service Starting...")
    print("📍 Server: http://localhost:3000")
    print("📖 API Docs: http://localhost:3000/docs")
    uvicorn.run(app, host="0.0.0.0", port=3000)
