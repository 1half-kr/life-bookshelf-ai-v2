"""
대화 맥락 관리 모듈
노년층과의 자연스러운 대화를 위한 맥락 추적 및 관리
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass
import re


@dataclass
class TopicTransition:
    """주제 전환 정보"""
    from_topic: str
    to_topic: str
    transition_reason: str
    timestamp: datetime
    user_initiated: bool


class ConversationContext(BaseModel):
    """대화 맥락 모델"""
    session_id: str
    current_topic: Optional[str] = None
    topic_depth: int = 0  # 현재 주제의 깊이 (1-5)
    emotional_state: str = "neutral"
    energy_level: str = "normal"  # low, normal, high
    engagement_level: str = "engaged"  # disengaged, neutral, engaged, very_engaged
    
    # 주제 관련
    topics_discussed: List[str] = []
    topic_transitions: List[TopicTransition] = []
    pending_topics: List[str] = []
    avoided_topics: List[str] = []
    
    # 기억 관련
    mentioned_people: Dict[str, Any] = {}  # 언급된 사람들
    mentioned_places: Dict[str, Any] = {}  # 언급된 장소들
    mentioned_events: Dict[str, Any] = {}  # 언급된 사건들
    time_references: List[Dict[str, Any]] = []  # 시간 참조
    
    # 대화 패턴
    response_patterns: Dict[str, int] = {}  # 응답 패턴 빈도
    question_preferences: List[str] = []  # 선호하는 질문 유형
    conversation_pace: str = "normal"  # slow, normal, fast
    
    # 감정 추적
    emotional_journey: List[Dict[str, Any]] = []
    comfort_level: int = 5  # 1-10 (편안함 정도)
    
    last_updated: datetime = datetime.now()


class ContextManager:
    """대화 맥락 관리자"""
    
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
        
        # 주제 관련 키워드 매핑
        self.topic_keywords = {
            "childhood": ["어린", "아이", "유년", "초등학교", "놀이", "부모님", "가족"],
            "school": ["학교", "공부", "선생님", "친구", "수업", "시험", "졸업"],
            "work": ["직장", "회사", "일", "동료", "상사", "업무", "은퇴"],
            "family": ["가족", "결혼", "아내", "남편", "자식", "아들", "딸"],
            "health": ["건강", "병원", "의사", "약", "아픈", "치료"],
            "hobbies": ["취미", "여가", "운동", "독서", "여행", "음악"]
        }
        
        # 감정 키워드 매핑
        self.emotion_keywords = {
            "happy": ["기쁜", "행복", "즐거운", "좋은", "웃음", "기뻐"],
            "sad": ["슬픈", "아픈", "힘든", "우울", "눈물", "서운"],
            "nostalgic": ["그리운", "옛날", "추억", "그때", "그시절"],
            "proud": ["자랑", "뿌듯", "성취", "보람", "자부심"],
            "worried": ["걱정", "불안", "염려", "근심", "두려운"]
        }
    
    def get_context(self, session_id: str) -> ConversationContext:
        """세션의 대화 맥락 조회"""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id=session_id)
        return self.contexts[session_id]
    
    def update_context_with_message(
        self,
        session_id: str,
        speaker: str,
        message: str,
        emotion: Optional[str] = None
    ) -> ConversationContext:
        """메시지를 바탕으로 맥락 업데이트"""
        
        context = self.get_context(session_id)
        
        if speaker == "user":
            # 사용자 메시지 분석
            self._analyze_user_message(context, message, emotion)
        else:
            # AI 메시지 분석
            self._analyze_ai_message(context, message)
        
        context.last_updated = datetime.now()
        return context
    
    def _analyze_user_message(
        self,
        context: ConversationContext,
        message: str,
        emotion: Optional[str] = None
    ):
        """사용자 메시지 분석"""
        
        # 주제 감지
        detected_topic = self._detect_topic(message)
        if detected_topic and detected_topic != context.current_topic:
            self._handle_topic_change(context, detected_topic, user_initiated=True)
        
        # 감정 상태 업데이트
        if emotion:
            context.emotional_state = emotion
        else:
            detected_emotion = self._detect_emotion(message)
            if detected_emotion:
                context.emotional_state = detected_emotion
        
        # 감정 여정 기록
        context.emotional_journey.append({
            "timestamp": datetime.now().isoformat(),
            "emotion": context.emotional_state,
            "trigger": message[:100],
            "speaker": "user"
        })
        
        # 언급된 인물, 장소, 사건 추출
        self._extract_entities(context, message)
        
        # 시간 참조 추출
        self._extract_time_references(context, message)
        
        # 참여도 평가
        self._assess_engagement(context, message)
        
        # 응답 패턴 분석
        self._analyze_response_pattern(context, message)
    
    def _analyze_ai_message(self, context: ConversationContext, message: str):
        """AI 메시지 분석"""
        
        # 질문 유형 분석
        question_type = self._analyze_question_type(message)
        if question_type:
            context.question_preferences.append(question_type)
            # 최근 10개만 유지
            context.question_preferences = context.question_preferences[-10:]
    
    def _detect_topic(self, message: str) -> Optional[str]:
        """메시지에서 주제 감지"""
        
        message_lower = message.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    
    def _detect_emotion(self, message: str) -> Optional[str]:
        """메시지에서 감정 감지"""
        
        message_lower = message.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return None
    
    def _handle_topic_change(
        self,
        context: ConversationContext,
        new_topic: str,
        user_initiated: bool = False
    ):
        """주제 변경 처리"""
        
        if context.current_topic:
            # 주제 전환 기록
            transition = TopicTransition(
                from_topic=context.current_topic,
                to_topic=new_topic,
                transition_reason="natural_flow" if user_initiated else "ai_guided",
                timestamp=datetime.now(),
                user_initiated=user_initiated
            )
            context.topic_transitions.append(transition)
        
        # 이전 주제를 논의된 주제에 추가
        if context.current_topic and context.current_topic not in context.topics_discussed:
            context.topics_discussed.append(context.current_topic)
        
        # 새 주제 설정
        context.current_topic = new_topic
        context.topic_depth = 1
        
        # 대기 중인 주제에서 제거
        if new_topic in context.pending_topics:
            context.pending_topics.remove(new_topic)
    
    def _extract_entities(self, context: ConversationContext, message: str):
        """인물, 장소, 사건 추출"""
        
        # 간단한 패턴 매칭으로 구현 (실제로는 NER 모델 사용 권장)
        
        # 인물 추출 (가족 관계 키워드)
        person_patterns = [
            r'(아버지|아빠|부친)',
            r'(어머니|엄마|모친)',
            r'(남편|아내|배우자)',
            r'(아들|딸|자식)',
            r'(형|누나|언니|동생)',
            r'(할아버지|할머니)',
            r'(손자|손녀)'
        ]
        
        for pattern in person_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if match not in context.mentioned_people:
                    context.mentioned_people[match] = {
                        "first_mentioned": datetime.now().isoformat(),
                        "mention_count": 1,
                        "contexts": [message[:100]]
                    }
                else:
                    context.mentioned_people[match]["mention_count"] += 1
                    context.mentioned_people[match]["contexts"].append(message[:100])
        
        # 장소 추출
        place_patterns = [
            r'(서울|부산|대구|인천|광주|대전|울산)',
            r'(고향|시골|동네|마을)',
            r'(학교|회사|병원|교회|절)',
            r'(집|댁|우리집)'
        ]
        
        for pattern in place_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if match not in context.mentioned_places:
                    context.mentioned_places[match] = {
                        "first_mentioned": datetime.now().isoformat(),
                        "mention_count": 1,
                        "contexts": [message[:100]]
                    }
                else:
                    context.mentioned_places[match]["mention_count"] += 1
                    context.mentioned_places[match]["contexts"].append(message[:100])
    
    def _extract_time_references(self, context: ConversationContext, message: str):
        """시간 참조 추출"""
        
        time_patterns = [
            r'(\d{4})년',
            r'(\d{1,2})살',
            r'(어린|젊은|중년|노년)?\s?(시절|때)',
            r'(초등학교|중학교|고등학교|대학교)?\s?(시절|때)',
            r'(결혼|취업|은퇴)\s?(전|후|할때|했을때)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                context.time_references.append({
                    "reference": match,
                    "context": message[:100],
                    "timestamp": datetime.now().isoformat()
                })
    
    def _assess_engagement(self, context: ConversationContext, message: str):
        """참여도 평가"""
        
        message_length = len(message)
        
        # 메시지 길이 기반 참여도 평가
        if message_length < 10:
            engagement = "disengaged"
        elif message_length < 50:
            engagement = "neutral"
        elif message_length < 150:
            engagement = "engaged"
        else:
            engagement = "very_engaged"
        
        context.engagement_level = engagement
        
        # 편안함 수준 조정
        if "..." in message or "음" in message or "글쎄" in message:
            context.comfort_level = max(1, context.comfort_level - 1)
        elif len(message) > 100 and any(emotion in message for emotion in ["좋", "행복", "기쁜"]):
            context.comfort_level = min(10, context.comfort_level + 1)
    
    def _analyze_response_pattern(self, context: ConversationContext, message: str):
        """응답 패턴 분석"""
        
        # 간단한 패턴 분류
        if message.endswith("?"):
            pattern = "question_back"
        elif len(message.split()) < 5:
            pattern = "short_response"
        elif "그런데" in message or "그리고" in message:
            pattern = "elaborative"
        elif "네" in message or "예" in message:
            pattern = "agreeable"
        else:
            pattern = "narrative"
        
        if pattern in context.response_patterns:
            context.response_patterns[pattern] += 1
        else:
            context.response_patterns[pattern] = 1
    
    def _analyze_question_type(self, message: str) -> Optional[str]:
        """질문 유형 분석"""
        
        if not message.endswith("?") and "?" not in message:
            return None
        
        if any(word in message for word in ["어떻게", "어떤", "무엇", "누구"]):
            return "open_ended"
        elif any(word in message for word in ["언제", "몇"]):
            return "specific_detail"
        elif any(word in message for word in ["기억", "생각"]):
            return "memory_recall"
        elif any(word in message for word in ["느낌", "기분"]):
            return "emotional"
        else:
            return "general"
    
    def get_conversation_insights(self, session_id: str) -> Dict[str, Any]:
        """대화 인사이트 제공"""
        
        context = self.get_context(session_id)
        
        return {
            "current_state": {
                "topic": context.current_topic,
                "emotional_state": context.emotional_state,
                "engagement_level": context.engagement_level,
                "comfort_level": context.comfort_level
            },
            "conversation_flow": {
                "topics_covered": len(context.topics_discussed),
                "topic_transitions": len(context.topic_transitions),
                "conversation_depth": context.topic_depth
            },
            "entities_mentioned": {
                "people": len(context.mentioned_people),
                "places": len(context.mentioned_places),
                "events": len(context.mentioned_events)
            },
            "emotional_journey": context.emotional_journey[-5:],  # 최근 5개
            "response_patterns": context.response_patterns,
            "recommendations": self._generate_recommendations(context)
        }
    
    def _generate_recommendations(self, context: ConversationContext) -> List[str]:
        """대화 진행 추천사항 생성"""
        
        recommendations = []
        
        # 참여도 기반 추천
        if context.engagement_level == "disengaged":
            recommendations.append("더 간단하고 구체적인 질문으로 전환하세요")
        elif context.engagement_level == "very_engaged":
            recommendations.append("현재 주제를 더 깊이 탐색해보세요")
        
        # 편안함 수준 기반 추천
        if context.comfort_level < 4:
            recommendations.append("더 가벼운 주제로 전환하거나 휴식을 제안하세요")
        elif context.comfort_level > 7:
            recommendations.append("더 개인적이고 깊은 주제를 탐색해볼 수 있습니다")
        
        # 주제 다양성 기반 추천
        if len(context.topics_discussed) < 3:
            recommendations.append("다양한 주제를 탐색해보세요")
        
        # 감정 상태 기반 추천
        if context.emotional_state in ["sad", "worried"]:
            recommendations.append("공감과 위로의 메시지를 포함하세요")
        elif context.emotional_state in ["happy", "proud"]:
            recommendations.append("긍정적인 감정을 더 탐색해보세요")
        
        return recommendations
    
    def suggest_next_questions(self, session_id: str) -> List[str]:
        """다음 질문 제안"""
        
        context = self.get_context(session_id)
        suggestions = []
        
        # 현재 주제 기반 제안
        if context.current_topic:
            if context.topic_depth < 3:
                suggestions.append(f"{context.current_topic}에 대해 더 자세히 들려주세요")
            else:
                suggestions.append("다른 관련된 경험도 있으신가요?")
        
        # 언급된 인물 기반 제안
        if context.mentioned_people:
            person = list(context.mentioned_people.keys())[0]
            suggestions.append(f"{person}과의 특별한 추억이 더 있으신가요?")
        
        # 감정 상태 기반 제안
        if context.emotional_state == "nostalgic":
            suggestions.append("그 시절이 많이 그리우시겠어요")
        elif context.emotional_state == "happy":
            suggestions.append("정말 행복한 시간이었겠네요")
        
        return suggestions[:3]  # 최대 3개 제안


# 전역 컨텍스트 매니저
_context_manager = None

def get_context_manager() -> ContextManager:
    """전역 컨텍스트 매니저 반환"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
