"""
대화 세션 관리 모듈
노년층과의 장시간 대화를 위한 세션 상태 관리
"""

import json
import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import redis
import asyncio


class ConversationMessage(BaseModel):
    """대화 메시지 모델"""
    message_id: str
    timestamp: datetime
    speaker: str  # "user" or "assistant"
    content: str
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = {}


class UserProfile(BaseModel):
    """사용자 프로필"""
    user_id: str
    name: str
    age: int
    gender: str
    birth_year: int
    hometown: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    family_info: Dict[str, Any] = {}
    health_info: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}


class ConversationSession(BaseModel):
    """대화 세션 모델"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    status: str  # "active", "paused", "completed", "expired"
    conversation_type: str  # "interview", "casual", "autobiography"
    current_topic: Optional[str] = None
    current_stage: str = "greeting"  # "greeting", "warming_up", "main_interview", "closing"
    messages: List[ConversationMessage] = []
    user_profile: Optional[UserProfile] = None
    session_metadata: Dict[str, Any] = {}


class SessionManager:
    """대화 세션 관리자"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        except:
            # Redis가 없는 경우 메모리 기반 저장소 사용
            self.redis_client = None
            self.memory_store = {}
        
        self.session_timeout = timedelta(hours=2)  # 2시간 세션 타임아웃
        self.max_messages_per_session = 1000  # 세션당 최대 메시지 수
    
    async def create_session(
        self,
        user_id: str,
        conversation_type: str = "interview",
        user_profile: Optional[UserProfile] = None
    ) -> ConversationSession:
        """새 대화 세션 생성"""
        
        session_id = f"session_{uuid.uuid4()}"
        now = datetime.now()
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            status="active",
            conversation_type=conversation_type,
            current_stage="greeting",
            user_profile=user_profile,
            session_metadata={
                "total_messages": 0,
                "topics_covered": [],
                "emotional_moments": [],
                "important_memories": []
            }
        )
        
        await self._save_session(session)
        
        # 환영 메시지 추가
        welcome_message = self._create_welcome_message(user_profile)
        await self.add_message(session_id, "assistant", welcome_message)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """세션 조회"""
        
        try:
            if self.redis_client:
                session_data = self.redis_client.get(f"session:{session_id}")
                if session_data:
                    data = json.loads(session_data)
                    return ConversationSession(**data)
            else:
                if session_id in self.memory_store:
                    return self.memory_store[session_id]
            
            return None
            
        except Exception as e:
            print(f"세션 조회 오류: {str(e)}")
            return None
    
    async def update_session(self, session: ConversationSession) -> bool:
        """세션 업데이트"""
        
        session.last_activity = datetime.now()
        return await self._save_session(session)
    
    async def add_message(
        self,
        session_id: str,
        speaker: str,
        content: str,
        emotion: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """메시지 추가"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        message = ConversationMessage(
            message_id=f"msg_{uuid.uuid4()}",
            timestamp=datetime.now(),
            speaker=speaker,
            content=content,
            emotion=emotion,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.session_metadata["total_messages"] += 1
        
        # 메시지 수 제한
        if len(session.messages) > self.max_messages_per_session:
            session.messages = session.messages[-self.max_messages_per_session:]
        
        # 감정적 순간 기록
        if emotion and emotion in ["sad", "happy", "nostalgic", "proud"]:
            session.session_metadata["emotional_moments"].append({
                "message_id": message.message_id,
                "emotion": emotion,
                "content_preview": content[:100],
                "timestamp": message.timestamp.isoformat()
            })
        
        return await self.update_session(session)
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """대화 기록 조회"""
        
        session = await self.get_session(session_id)
        if not session:
            return []
        
        return session.messages[-limit:] if limit > 0 else session.messages
    
    async def update_session_stage(
        self,
        session_id: str,
        new_stage: str,
        topic: Optional[str] = None
    ) -> bool:
        """세션 단계 업데이트"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.current_stage = new_stage
        if topic:
            session.current_topic = topic
            
            # 다룬 주제 기록
            if topic not in session.session_metadata["topics_covered"]:
                session.session_metadata["topics_covered"].append(topic)
        
        return await self.update_session(session)
    
    async def mark_important_memory(
        self,
        session_id: str,
        message_id: str,
        memory_type: str,
        significance: int = 5
    ) -> bool:
        """중요한 기억 표시"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # 해당 메시지 찾기
        message = next(
            (msg for msg in session.messages if msg.message_id == message_id),
            None
        )
        
        if message:
            session.session_metadata["important_memories"].append({
                "message_id": message_id,
                "memory_type": memory_type,
                "significance": significance,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            })
            
            return await self.update_session(session)
        
        return False
    
    async def pause_session(self, session_id: str) -> bool:
        """세션 일시정지"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.status = "paused"
        return await self.update_session(session)
    
    async def resume_session(self, session_id: str) -> bool:
        """세션 재개"""
        
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.status = "active"
        return await self.update_session(session)
    
    async def complete_session(self, session_id: str) -> Dict[str, Any]:
        """세션 완료 및 요약"""
        
        session = await self.get_session(session_id)
        if not session:
            return {"success": False, "error": "세션을 찾을 수 없습니다."}
        
        session.status = "completed"
        
        # 세션 요약 생성
        summary = {
            "session_id": session_id,
            "duration": (session.last_activity - session.created_at).total_seconds() / 60,  # 분 단위
            "total_messages": len(session.messages),
            "topics_covered": session.session_metadata.get("topics_covered", []),
            "emotional_moments": len(session.session_metadata.get("emotional_moments", [])),
            "important_memories": len(session.session_metadata.get("important_memories", [])),
            "completion_time": datetime.now().isoformat()
        }
        
        await self.update_session(session)
        
        return {"success": True, "summary": summary}
    
    async def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리"""
        
        cleaned_count = 0
        
        if self.redis_client:
            # Redis에서 만료된 세션 찾기 (실제 구현에서는 더 효율적인 방법 사용)
            pass
        else:
            # 메모리 저장소에서 만료된 세션 정리
            now = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.memory_store.items():
                if now - session.last_activity > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.memory_store[session_id]
                cleaned_count += 1
        
        return cleaned_count
    
    def _create_welcome_message(self, user_profile: Optional[UserProfile]) -> str:
        """환영 메시지 생성"""
        
        if user_profile and user_profile.name:
            return f"안녕하세요, {user_profile.name}님! 오늘 소중한 시간을 내어 주셔서 감사합니다. 편안하게 이야기를 나누어 보아요."
        else:
            return "안녕하세요! 오늘 소중한 시간을 내어 주셔서 감사합니다. 편안하게 이야기를 나누어 보아요."
    
    async def _save_session(self, session: ConversationSession) -> bool:
        """세션 저장"""
        
        try:
            if self.redis_client:
                session_data = session.json()
                self.redis_client.setex(
                    f"session:{session.session_id}",
                    int(self.session_timeout.total_seconds()),
                    session_data
                )
            else:
                self.memory_store[session.session_id] = session
            
            return True
            
        except Exception as e:
            print(f"세션 저장 오류: {str(e)}")
            return False


# 전역 세션 매니저
_session_manager = None

def get_session_manager() -> SessionManager:
    """전역 세션 매니저 반환"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
