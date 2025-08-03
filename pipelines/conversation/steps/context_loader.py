"""
Context loading step for conversation pipeline
"""
from typing import Dict, Any, List, Optional
import json

from shared.models.pipeline import PipelineStep, StepContext, StepResult, StepStatus
from shared.models.data import ConversationSession, Message, UserProfile


class ContextLoaderStep(PipelineStep):
    """Loads conversation context and session history"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("context_loader", config)
        self.max_context_messages = self.get_config("max_context_messages", 10)
        self.session_timeout_hours = self.get_config("session_timeout_hours", 2)
    
    async def execute(self, context: StepContext) -> StepResult:
        """Execute context loading"""
        try:
            session_id = context.input_data["validated_session_id"]
            user_profile = context.input_data["validated_user_profile"]
            
            # Load or create conversation session
            session = await self._load_or_create_session(session_id, user_profile)
            
            # Get conversation context
            conversation_context = self._build_conversation_context(session)
            
            # Get user generation context
            generation_context = self._build_generation_context(user_profile)
            
            # Get historical context
            historical_context = self._build_historical_context(user_profile)
            
            return StepResult(
                step_name=self.name,
                status=StepStatus.COMPLETED,
                output_data={
                    "conversation_session": session,
                    "conversation_context": conversation_context,
                    "generation_context": generation_context,
                    "historical_context": historical_context,
                    "is_new_session": len(session.messages) == 0
                },
                metadata={
                    "session_message_count": len(session.messages),
                    "context_messages_loaded": min(len(session.messages), self.max_context_messages),
                    "user_generation": user_profile.generation,
                    "user_birth_decade": user_profile.birth_decade
                }
            )
            
        except Exception as e:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error_message=f"Context loading error: {str(e)}"
            )
    
    async def _load_or_create_session(
        self, 
        session_id: str, 
        user_profile: UserProfile
    ) -> ConversationSession:
        """Load existing session or create new one"""
        # In a real implementation, this would load from Redis/Database
        # For now, we'll simulate with in-memory storage
        
        # Try to load existing session (simulated)
        existing_session = await self._load_session_from_storage(session_id)
        
        if existing_session:
            # Check if session is still valid
            if self._is_session_valid(existing_session):
                return existing_session
            else:
                # Session expired, create new one
                return ConversationSession(
                    session_id=session_id,
                    user_profile=user_profile
                )
        else:
            # Create new session
            return ConversationSession(
                session_id=session_id,
                user_profile=user_profile
            )
    
    async def _load_session_from_storage(self, session_id: str) -> Optional[ConversationSession]:
        """Load session from storage (Redis/Database)"""
        # This is a placeholder - in real implementation:
        # 1. Connect to Redis/Database
        # 2. Load session data
        # 3. Deserialize to ConversationSession object
        return None
    
    def _is_session_valid(self, session: ConversationSession) -> bool:
        """Check if session is still valid"""
        from datetime import datetime, timedelta
        
        if not session.is_active:
            return False
        
        timeout = timedelta(hours=self.session_timeout_hours)
        return (datetime.utcnow() - session.last_activity) < timeout
    
    def _build_conversation_context(self, session: ConversationSession) -> Dict[str, Any]:
        """Build conversation context from session history"""
        recent_messages = session.messages[-self.max_context_messages:]
        
        # Extract conversation topics
        topics = self._extract_conversation_topics(recent_messages)
        
        # Calculate conversation statistics
        user_messages = [msg for msg in recent_messages if msg.is_from_user]
        avg_message_length = (
            sum(msg.word_count for msg in user_messages) / len(user_messages)
            if user_messages else 0
        )
        
        return {
            "recent_messages": [
                {
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "word_count": msg.word_count
                }
                for msg in recent_messages
            ],
            "conversation_topics": topics,
            "total_messages": len(session.messages),
            "user_message_count": len([msg for msg in session.messages if msg.is_from_user]),
            "avg_message_length": avg_message_length,
            "conversation_duration_minutes": (
                (session.last_activity - session.created_at).total_seconds() / 60
            ),
            "session_context": session.context
        }
    
    def _build_generation_context(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Build generation-specific context"""
        return {
            "generation": user_profile.generation,
            "birth_decade": user_profile.birth_decade,
            "age_group": self._get_age_group(user_profile.age),
            "life_stage": "elderly",
            "cultural_context": self._get_cultural_context(user_profile.birth_decade)
        }
    
    def _build_historical_context(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Build historical context based on user's generation"""
        decade = user_profile.birth_decade
        
        historical_contexts = {
            "1920s": {
                "major_events": ["일제강점기", "태평양전쟁"],
                "social_context": "식민지 시대, 전통 사회",
                "keywords": ["일본", "조선", "식민지", "전통"]
            },
            "1930s": {
                "major_events": ["일제강점기 말기", "해방"],
                "social_context": "전쟁과 해방의 시대",
                "keywords": ["해방", "광복", "혼란", "희망"]
            },
            "1940s": {
                "major_events": ["한국전쟁", "분단"],
                "social_context": "전쟁과 재건의 시대",
                "keywords": ["전쟁", "피난", "분단", "재건"]
            },
            "1950s": {
                "major_events": ["전후 복구", "산업화 시작"],
                "social_context": "복구와 발전의 시대",
                "keywords": ["복구", "발전", "희망", "근대화"]
            },
            "1960s": {
                "major_events": ["경제개발", "새마을운동"],
                "social_context": "고도성장의 시대",
                "keywords": ["개발", "성장", "새마을", "도시화"]
            }
        }
        
        return historical_contexts.get(decade, {
            "major_events": ["현대사"],
            "social_context": "현대 사회",
            "keywords": ["현대", "발전"]
        })
    
    def _extract_conversation_topics(self, messages: List[Message]) -> List[str]:
        """Extract topics from conversation messages"""
        topics = set()
        
        topic_keywords = {
            "family": ["가족", "부모", "아버지", "어머니", "형제", "자매", "배우자", "자녀"],
            "childhood": ["어린 시절", "어렸을 때", "유년기", "놀이", "학교"],
            "work": ["직장", "일", "회사", "직업", "근무", "사업"],
            "war": ["전쟁", "피난", "6.25", "부산", "대구"],
            "marriage": ["결혼", "신랑", "신부", "혼례", "배우자"],
            "health": ["건강", "병원", "의사", "치료", "약"],
            "hobbies": ["취미", "여가", "놀이", "운동", "독서"]
        }
        
        for message in messages:
            if message.is_from_user:
                content = message.content.lower()
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        topics.add(topic)
        
        return list(topics)
    
    def _get_age_group(self, age: int) -> str:
        """Get age group classification"""
        if 65 <= age < 75:
            return "young_elderly"
        elif 75 <= age < 85:
            return "middle_elderly"
        else:
            return "old_elderly"
    
    def _get_cultural_context(self, birth_decade: str) -> Dict[str, Any]:
        """Get cultural context for the birth decade"""
        cultural_contexts = {
            "1920s": {"education": "한학", "values": "유교적", "lifestyle": "농업 중심"},
            "1930s": {"education": "일제교육", "values": "전통과 근대", "lifestyle": "도시화 시작"},
            "1940s": {"education": "해방 후 교육", "values": "자유와 희망", "lifestyle": "재건 노력"},
            "1950s": {"education": "근대 교육", "values": "발전 의지", "lifestyle": "도시 생활"},
            "1960s": {"education": "현대 교육", "values": "성장 지향", "lifestyle": "중산층 형성"}
        }
        
        return cultural_contexts.get(birth_decade, {
            "education": "현대 교육",
            "values": "현대적",
            "lifestyle": "현대 생활"
        })
