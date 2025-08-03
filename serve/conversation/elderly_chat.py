"""
노년층 특화 대화 로직
노년층의 특성을 고려한 대화 흐름 및 응답 생성
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

# 절대 경로로 모듈 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
serve_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(serve_dir)
sys.path.insert(0, serve_dir)
sys.path.insert(0, project_dir)

try:
    from .session_manager import SessionManager
    from .context_manager import ContextManager
    from ..llm.bedrock_client import BedrockClient
except ImportError:
    # 절대 경로로 fallback
    from conversation.session_manager import SessionManager
    from conversation.context_manager import ContextManager
    from llm.bedrock_client import BedrockClient


class ElderlyChat:
    """노년층 특화 대화 관리자"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.context_manager = ContextManager()
    async def generate_welcome_message(self, user_profile: Dict[str, Any], conversation_type: str = "interview") -> tuple:
        """사용자 프로필에 맞는 환영 메시지와 추천 주제 생성"""
        try:
            name = user_profile.get("name", "어르신")
            age = user_profile.get("age", 70)
            
            welcome_prompt = f"""
            {age}세 {name}님을 위한 따뜻하고 정중한 환영 메시지를 생성해주세요.
            자서전 작성 과정에 대한 간단한 설명과 함께 편안한 분위기를 조성해주세요.
            존댓말을 사용하고, 노년층에게 적합한 톤으로 작성해주세요.
            길이는 2-3문장 정도로 간결하게 해주세요.
            """
            
            response = await self.bedrock_client.generate_response(
                prompt=welcome_prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            welcome_message = response if response else f"{name}님, 안녕하세요. 소중한 인생 이야기를 들려주시면 아름다운 자서전으로 만들어드리겠습니다."
            
            # 추천 주제 생성
            suggested_topics = [
                "어린 시절 추억",
                "가족과의 소중한 시간",
                "인생의 전환점",
                "가장 기억에 남는 순간",
                "후손들에게 전하고 싶은 말씀"
            ]
            
            return welcome_message, suggested_topics
            
        except Exception as e:
            name = user_profile.get("name", "어르신")
            welcome_message = f"{name}님, 안녕하세요. 소중한 인생 이야기를 들려주시면 아름다운 자서전으로 만들어드리겠습니다."
            suggested_topics = ["어린 시절 추억", "가족 이야기", "인생의 지혜"]
            return welcome_message, suggested_topics

    async def generate_response(
        self,
        user_input: str,
        context: Dict[str, Any],
        emotion_result: Dict[str, Any] = None,
        memory_result: Dict[str, Any] = None
    ) -> str:
        """노년층 특화 AI 응답 생성"""
        try:
            user_profile = context.get("user_profile", {})
            name = user_profile.get("name", "어르신")
            age = user_profile.get("age", 70)
            
            # 시스템 프롬프트 구성
            system_prompt = f"""
            당신은 {age}세 {name}님과 대화하는 노년층 전문 자서전 작성 도우미입니다.
            
            대화 원칙:
            1. 항상 존댓말을 사용하세요
            2. 따뜻하고 공감적인 톤을 유지하세요
            3. 노년층의 경험을 존중하고 격려하세요
            4. 구체적이고 깊이 있는 후속 질문을 하세요
            5. 감정에 공감하며 응답하세요
            
            현재 감정 상태: {emotion_result.get('primary_emotion', '평온') if emotion_result else '평온'}
            기억 유형: {memory_result.get('memory_type', '일반') if memory_result else '일반'}
            """
            
            # 사용자 입력에 대한 응답 생성
            response_prompt = f"""
            사용자 말씀: "{user_input}"
            
            위 말씀에 대해 공감하며 응답하고, 더 자세한 이야기를 들을 수 있는 
            자연스러운 후속 질문을 1-2개 포함해주세요.
            응답은 3-4문장 정도로 적절한 길이로 해주세요.
            """
            
            response = await self.bedrock_client.generate_response(
                prompt=response_prompt,
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.8
            )
            
            return response if response else "말씀해주신 이야기가 정말 소중합니다. 더 자세히 들려주실 수 있을까요?"
            
        except Exception as e:
            return "말씀해주신 이야기에 감사드립니다. 더 자세한 내용을 들려주시면 좋겠습니다."
        
        # 대화 단계별 전략
        self.conversation_strategies = {
            "greeting": self._handle_greeting_stage,
            "warming_up": self._handle_warming_up_stage,
            "main_interview": self._handle_main_interview_stage,
            "deep_exploration": self._handle_deep_exploration_stage,
            "closing": self._handle_closing_stage
        }
        
        # 노년층 대화 원칙
        self.conversation_principles = {
            "pace": "slow_and_gentle",
            "tone": "respectful_and_warm",
            "approach": "patient_and_understanding",
            "focus": "life_experiences_and_wisdom"
        }
    
    async def process_user_message(
        self,
        session_id: str,
        user_message: str,
        emotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """사용자 메시지 처리 및 응답 생성"""
        
        try:
            # 세션 조회
            session = await self.session_manager.get_session(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "세션을 찾을 수 없습니다."
                }
            
            # 사용자 메시지 저장
            await self.session_manager.add_message(
                session_id, "user", user_message, emotion
            )
            
            # 대화 맥락 업데이트
            context = self.context_manager.update_context_with_message(
                session_id, "user", user_message, emotion
            )
            
            # 현재 단계에 따른 응답 생성
            response_data = await self.conversation_strategies[session.current_stage](
                session, context, user_message
            )
            
            # AI 응답 저장
            await self.session_manager.add_message(
                session_id, "assistant", response_data["response"], 
                response_data.get("emotion")
            )
            
            # 맥락 업데이트
            self.context_manager.update_context_with_message(
                session_id, "assistant", response_data["response"]
            )
            
            return {
                "success": True,
                "response": response_data["response"],
                "emotion": response_data.get("emotion", "gentle"),
                "stage": session.current_stage,
                "next_stage": response_data.get("next_stage"),
                "suggestions": response_data.get("suggestions", []),
                "context_insights": self.context_manager.get_conversation_insights(session_id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"대화 처리 중 오류가 발생했습니다: {str(e)}"
            }
    
    async def _handle_greeting_stage(
        self,
        session,
        context,
        user_message: str
    ) -> Dict[str, Any]:
        """인사 단계 처리"""
        
        # 사용자 프로필 정보 수집
        if not session.user_profile or not session.user_profile.name:
            response = await self._collect_basic_info(user_message)
            return {
                "response": response,
                "emotion": "warm",
                "next_stage": "warming_up" if "이름" in user_message else "greeting"
            }
        
        # 따뜻한 인사와 함께 다음 단계로
        response = f"반갑습니다, {session.user_profile.name}님. 오늘 이렇게 소중한 시간을 함께 할 수 있어서 정말 기쁩니다. 편안하게 대화를 나누어 보아요."
        
        await self.session_manager.update_session_stage(session.session_id, "warming_up")
        
        return {
            "response": response,
            "emotion": "warm",
            "next_stage": "warming_up"
        }
    
    async def _handle_warming_up_stage(
        self,
        session,
        context,
        user_message: str
    ) -> Dict[str, Any]:
        """워밍업 단계 처리"""
        
        # 편안한 주제로 시작
        warming_topics = [
            "오늘 기분은 어떠세요?",
            "요즘 어떻게 지내고 계세요?",
            "건강은 괜찮으신가요?",
            "날씨가 참 좋네요. 이런 날씨를 좋아하세요?"
        ]
        
        # 사용자의 편안함 수준 확인
        if context.comfort_level >= 6:
            # 본격적인 인터뷰로 전환
            response = "그렇군요. 이제 조금 더 깊은 이야기를 나누어 볼까요? 어린 시절 이야기부터 시작해보면 어떨까요?"
            
            await self.session_manager.update_session_stage(
                session.session_id, "main_interview", "childhood"
            )
            
            return {
                "response": response,
                "emotion": "encouraging",
                "next_stage": "main_interview"
            }
        else:
            # 더 편안하게 만들기
            response = "천천히 편안하게 이야기하시면 됩니다. 급할 것 없어요."
            
            return {
                "response": response,
                "emotion": "reassuring",
                "next_stage": "warming_up"
            }
    
    async def _handle_main_interview_stage(
        self,
        session,
        context,
        user_message: str
    ) -> Dict[str, Any]:
        """주요 인터뷰 단계 처리"""
        
        # 현재 주제에 따른 질문 생성
        current_topic = context.current_topic or "childhood"
        
        # 사용자 프로필 정보 준비
        user_profile = session.user_profile
        age = user_profile.age if user_profile else 70
        gender = user_profile.gender if user_profile else "여성"
        
        # 시대적 맥락 추가
        birth_decade = self._get_birth_decade(age)
        historical_context = self._get_historical_context(birth_decade)
        
        # 대화 히스토리 준비
        recent_messages = await self.session_manager.get_conversation_history(
            session.session_id, limit=10
        )
        conversation_history = "\n".join([
            f"{msg.speaker}: {msg.content}" for msg in recent_messages[-5:]
        ])
        
        # 프롬프트 생성
        prompt_input = {
            "age": age,
            "gender": gender,
            "current_situation": f"{age}세 {gender}",
            "topic": current_topic,
            "conversation_history": conversation_history,
            "user_response": user_message
        }
        
        # Bedrock을 통한 응답 생성
        system_prompt = f"""
        당신은 노년층의 소중한 인생 이야기를 듣는 전문 인터뷰어입니다.
        
        대화 원칙:
        1. 존댓말을 사용하고 정중하고 따뜻한 어조를 유지하세요
        2. 천천히, 명확하게 질문하세요
        3. 사용자의 감정에 공감하고 격려하세요
        4. 구체적인 기억과 감정을 자연스럽게 이끌어내세요
        5. 시대적 배경: {historical_context}
        
        현재 주제: {current_topic}
        사용자 연령: {age}세
        """
        
        response = await self.bedrock_client.generate_response(
            prompt=f"사용자 응답: {user_message}\n\n적절한 후속 질문이나 공감 응답을 생성해주세요.",
            system_prompt=system_prompt
        )
        
        # 감정 분석
        emotion_analysis = await self.bedrock_client.analyze_emotion(user_message)
        
        # 중요한 기억인지 판단
        if emotion_analysis.get("significance", 0) >= 7:
            # 중요한 기억으로 표시
            last_message = recent_messages[-1] if recent_messages else None
            if last_message:
                await self.session_manager.mark_important_memory(
                    session.session_id,
                    last_message.message_id,
                    "significant_memory",
                    emotion_analysis.get("significance", 5)
                )
        
        # 주제 깊이 증가
        if context.topic_depth < 5:
            context.topic_depth += 1
        else:
            # 새로운 주제로 전환 제안
            next_topic = self._suggest_next_topic(context, session.user_profile)
            if next_topic:
                await self.session_manager.update_session_stage(
                    session.session_id, "main_interview", next_topic
                )
        
        return {
            "response": response,
            "emotion": self._determine_response_emotion(emotion_analysis),
            "next_stage": "main_interview",
            "suggestions": self.context_manager.suggest_next_questions(session.session_id)
        }
    
    async def _handle_deep_exploration_stage(
        self,
        session,
        context,
        user_message: str
    ) -> Dict[str, Any]:
        """심화 탐색 단계 처리"""
        
        # 감정적으로 의미 있는 순간들을 더 깊이 탐색
        system_prompt = """
        사용자가 중요한 기억이나 감정적인 경험을 공유하고 있습니다.
        이를 더 깊이 탐색하되, 부담스럽지 않게 접근하세요.
        
        접근 방식:
        1. 그 순간의 감정을 구체적으로 탐색
        2. 주변 사람들의 반응이나 상황
        3. 그 경험이 인생에 미친 영향
        4. 현재 시점에서의 생각과 느낌
        """
        
        response = await self.bedrock_client.generate_response(
            prompt=user_message,
            system_prompt=system_prompt
        )
        
        return {
            "response": response,
            "emotion": "empathetic",
            "next_stage": "deep_exploration"
        }
    
    async def _handle_closing_stage(
        self,
        session,
        context,
        user_message: str
    ) -> Dict[str, Any]:
        """마무리 단계 처리"""
        
        # 대화 요약 및 감사 인사
        session_summary = await self.session_manager.complete_session(session.session_id)
        
        response = f"""
        오늘 정말 소중한 이야기들을 들려주셔서 감사합니다, {session.user_profile.name if session.user_profile else ''}님.
        
        {len(context.topics_discussed)}개의 주제에 대해 깊이 있는 대화를 나누었고,
        특히 {', '.join(context.topics_discussed[:3])}에 대한 이야기가 인상 깊었습니다.
        
        오늘 나누신 이야기들이 소중한 자서전의 한 부분이 될 것입니다.
        다음에 또 뵙겠습니다.
        """
        
        return {
            "response": response,
            "emotion": "grateful",
            "next_stage": "completed",
            "session_summary": session_summary
        }
    
    async def _collect_basic_info(self, user_message: str) -> str:
        """기본 정보 수집"""
        
        if "이름" not in user_message and "저는" not in user_message:
            return "안녕하세요! 먼저 성함을 알려주시겠어요?"
        
        # 간단한 이름 추출 (실제로는 더 정교한 NER 사용)
        name = self._extract_name(user_message)
        if name:
            return f"반갑습니다, {name}님! 연세는 어떻게 되시나요?"
        
        return "성함을 다시 한 번 말씀해 주시겠어요?"
    
    def _extract_name(self, message: str) -> Optional[str]:
        """메시지에서 이름 추출 (간단한 패턴 매칭)"""
        
        import re
        
        # "저는 김철수입니다" 패턴
        pattern1 = r'저는\s*([가-힣]{2,4})'
        match1 = re.search(pattern1, message)
        if match1:
            return match1.group(1)
        
        # "이름은 김철수" 패턴
        pattern2 = r'이름은\s*([가-힣]{2,4})'
        match2 = re.search(pattern2, message)
        if match2:
            return match2.group(1)
        
        return None
    
    def _get_birth_decade(self, age: int) -> str:
        """연령으로부터 출생 연대 계산"""
        
        current_year = datetime.now().year
        birth_year = current_year - age
        decade = (birth_year // 10) * 10
        
        return f"{decade}s"
    
    def _get_historical_context(self, birth_decade: str) -> str:
        """출생 연대에 따른 역사적 맥락 반환"""
        
        # historical_context.json에서 해당 시대 정보 조회
        # 여기서는 간단한 예시
        context_map = {
            "1930s": "일제강점기, 전쟁의 시대",
            "1940s": "광복과 한국전쟁, 격동의 시대",
            "1950s": "전후 복구와 산업화 시작",
            "1960s": "경제개발과 근대화",
            "1970s": "고도성장과 중산층 형성"
        }
        
        return context_map.get(birth_decade, "현대사의 증인")
    
    def _suggest_next_topic(self, context, user_profile) -> Optional[str]:
        """다음 주제 제안"""
        
        # 아직 다루지 않은 주요 주제들
        major_topics = ["childhood", "school", "work", "family", "health", "wisdom"]
        
        for topic in major_topics:
            if topic not in context.topics_discussed:
                return topic
        
        return None
    
    def _determine_response_emotion(self, emotion_analysis: Dict[str, Any]) -> str:
        """응답 감정 결정"""
        
        primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
        
        emotion_mapping = {
            "기쁨": "warm",
            "슬픔": "empathetic", 
            "그리움": "gentle",
            "자부심": "encouraging",
            "후회": "understanding",
            "감사": "warm"
        }
        
        return emotion_mapping.get(primary_emotion, "gentle")
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """대화 요약 생성"""
        
        session = await self.session_manager.get_session(session_id)
        context = self.context_manager.get_context(session_id)
        
        if not session:
            return {"error": "세션을 찾을 수 없습니다."}
        
        # 중요한 기억들 추출
        important_memories = session.session_metadata.get("important_memories", [])
        
        # 감정적 순간들 추출
        emotional_moments = session.session_metadata.get("emotional_moments", [])
        
        # 언급된 인물들
        mentioned_people = list(context.mentioned_people.keys())
        
        return {
            "session_duration": (session.last_activity - session.created_at).total_seconds() / 60,
            "total_messages": len(session.messages),
            "topics_covered": context.topics_discussed,
            "important_memories_count": len(important_memories),
            "emotional_moments_count": len(emotional_moments),
            "mentioned_people": mentioned_people,
            "overall_emotional_tone": context.emotional_state,
            "engagement_level": context.engagement_level,
            "key_insights": important_memories[:5]  # 상위 5개 중요 기억
        }


# 전역 대화 관리자
_conversation_manager = None

def get_elderly_conversation_manager() -> ElderlyChat:
    """전역 노년층 대화 관리자 반환"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ElderlyChat()
    return _conversation_manager
