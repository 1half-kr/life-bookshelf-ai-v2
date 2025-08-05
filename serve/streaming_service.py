"""
Streaming Response Service - 실시간 응답 스트리밍
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StreamingService:
    """실시간 응답 스트리밍 서비스"""
    
    def __init__(self):
        self.active_streams = {}
        logger.info("Streaming Service 초기화 완료")
    
    async def stream_ai_response(self, response_text: str, session_id: str, 
                               chunk_size: int = 10, delay: float = 0.05) -> AsyncGenerator[str, None]:
        """AI 응답을 실시간으로 스트리밍"""
        try:
            self.active_streams[session_id] = True
            
            # 시작 이벤트
            yield f"data: {json.dumps({'type': 'start', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            
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
    
    async def stream_follow_up_questions(self, questions: list, session_id: str) -> AsyncGenerator[str, None]:
        """후속 질문들을 순차적으로 스트리밍"""
        try:
            for i, question_data in enumerate(questions):
                question_event = {
                    "type": "follow_up_question",
                    "question": question_data["question"],
                    "category": question_data.get("category", "general"),
                    "score": question_data.get("score", 0.8),
                    "index": i + 1,
                    "total": len(questions),
                    "session_id": session_id
                }
                
                yield f"data: {json.dumps(question_event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.3)  # 질문 간 간격
                
        except Exception as e:
            logger.error(f"후속 질문 스트리밍 오류: {e}")
    
    async def stream_conversation_analysis(self, analysis_data: Dict[str, Any], 
                                         session_id: str) -> AsyncGenerator[str, None]:
        """대화 분석 결과를 스트리밍"""
        try:
            # 유사 경험 수
            if "similar_experiences_count" in analysis_data:
                similar_event = {
                    "type": "similar_experiences",
                    "count": analysis_data["similar_experiences_count"],
                    "session_id": session_id
                }
                yield f"data: {json.dumps(similar_event)}\n\n"
                await asyncio.sleep(0.2)
            
            # 개인화 점수
            if "personalization_score" in analysis_data:
                personalization_event = {
                    "type": "personalization_score",
                    "score": analysis_data["personalization_score"],
                    "session_id": session_id
                }
                yield f"data: {json.dumps(personalization_event)}\n\n"
                
        except Exception as e:
            logger.error(f"분석 결과 스트리밍 오류: {e}")
    
    def stop_stream(self, session_id: str) -> bool:
        """특정 세션의 스트리밍 중단"""
        if session_id in self.active_streams:
            del self.active_streams[session_id]
            logger.info(f"스트리밍 중단: {session_id}")
            return True
        return False
    
    def get_active_streams(self) -> Dict[str, bool]:
        """현재 활성 스트림 목록"""
        return self.active_streams.copy()
    
    async def stream_typing_indicator(self, session_id: str, duration: float = 2.0) -> AsyncGenerator[str, None]:
        """타이핑 인디케이터 스트리밍"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                if session_id not in self.active_streams:
                    break
                
                typing_event = {
                    "type": "typing",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                yield f"data: {json.dumps(typing_event)}\n\n"
                await asyncio.sleep(0.5)
            
            # 타이핑 종료
            typing_end_event = {
                "type": "typing_end",
                "session_id": session_id
            }
            yield f"data: {json.dumps(typing_end_event)}\n\n"
            
        except Exception as e:
            logger.error(f"타이핑 인디케이터 오류: {e}")

# 전역 인스턴스
streaming_service = None

def get_streaming_service() -> StreamingService:
    """Streaming Service 싱글톤 인스턴스 반환"""
    global streaming_service
    if streaming_service is None:
        streaming_service = StreamingService()
    return streaming_service
