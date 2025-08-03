"""
LLM processing step for conversation pipeline
"""
import json
from typing import Dict, Any, Optional
import time

from shared.models.pipeline import PipelineStep, StepContext, StepResult, StepStatus
from shared.models.data import UserProfile, ConversationSession


class LLMProcessorStep(PipelineStep):
    """Processes user message through LLM to generate AI response"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("llm_processor", config)
        self.model_id = self.get_config("model_id", "claude-3-sonnet-20240229")
        self.fallback_model_id = self.get_config("fallback_model_id", "claude-3-haiku-20240307")
        self.max_tokens = self.get_config("max_tokens", 1000)
        self.temperature = self.get_config("temperature", 0.7)
        self.timeout_seconds = self.get_config("timeout_seconds", 30)
    
    async def execute(self, context: StepContext) -> StepResult:
        """Execute LLM processing"""
        try:
            start_time = time.time()
            
            # Extract input data
            user_message = context.input_data["validated_message"]
            user_profile = context.input_data["validated_user_profile"]
            conversation_context = context.input_data["conversation_context"]
            generation_context = context.input_data["generation_context"]
            historical_context = context.input_data["historical_context"]
            is_new_session = context.input_data["is_new_session"]
            
            # Build LLM prompt
            prompt = self._build_elderly_optimized_prompt(
                user_message=user_message,
                user_profile=user_profile,
                conversation_context=conversation_context,
                generation_context=generation_context,
                historical_context=historical_context,
                is_new_session=is_new_session
            )
            
            # Generate AI response
            ai_response = await self._generate_ai_response(prompt)
            
            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(
                user_message, user_profile, conversation_context
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return StepResult(
                step_name=self.name,
                status=StepStatus.COMPLETED,
                output_data={
                    "ai_response": ai_response["content"],
                    "follow_up_questions": follow_up_questions,
                    "model_used": ai_response["model_id"],
                    "token_usage": ai_response["token_usage"],
                    "llm_processing_time": processing_time
                },
                metadata={
                    "prompt_length": len(prompt),
                    "response_length": len(ai_response["content"]),
                    "model_id": ai_response["model_id"],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            )
            
        except Exception as e:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error_message=f"LLM processing error: {str(e)}"
            )
    
    def _build_elderly_optimized_prompt(
        self,
        user_message: str,
        user_profile: UserProfile,
        conversation_context: Dict[str, Any],
        generation_context: Dict[str, Any],
        historical_context: Dict[str, Any],
        is_new_session: bool
    ) -> str:
        """Build elderly-optimized prompt for LLM"""
        
        # Base system prompt for elderly conversation
        system_prompt = f"""당신은 65세 이상 노년층을 위한 전문 대화 상대입니다. 
다음 특성을 가지고 대화해주세요:

1. 존댓말을 사용하고 정중하고 따뜻한 어조로 대화
2. 노년층의 경험과 지혜를 존중하고 공감
3. 천천히, 명확하게 설명
4. 감정적 공감과 이해 표현
5. 기억을 회상할 수 있도록 도움
6. 적절한 후속 질문으로 대화 이어가기

사용자 정보:
- 이름: {user_profile.name}
- 나이: {user_profile.age}세
- 성별: {user_profile.gender}
- 세대: {generation_context['generation']}
- 출생 연대: {generation_context['birth_decade']}

역사적 맥락:
- 주요 사건: {', '.join(historical_context.get('major_events', []))}
- 사회적 배경: {historical_context.get('social_context', '')}
"""
        
        # Add conversation history if not new session
        if not is_new_session and conversation_context['recent_messages']:
            system_prompt += "\n\n최근 대화 내용:\n"
            for msg in conversation_context['recent_messages'][-3:]:  # Last 3 messages
                sender = "사용자" if msg['sender'] == "user" else "AI"
                system_prompt += f"{sender}: {msg['content']}\n"
        
        # Add conversation topics if available
        if conversation_context.get('conversation_topics'):
            topics = ', '.join(conversation_context['conversation_topics'])
            system_prompt += f"\n현재까지 대화 주제: {topics}\n"
        
        # User's current message
        user_prompt = f"\n사용자의 현재 메시지: {user_message}\n"
        
        # Response guidelines
        response_guidelines = """
응답 가이드라인:
1. 사용자의 이야기에 공감하고 격려
2. 관련된 추가 질문으로 더 많은 이야기 유도
3. 노년층 언어 패턴에 맞는 자연스러운 대화
4. 200-300자 내외의 적절한 길이
5. 따뜻하고 친근한 어조 유지

이제 {user_profile.name}님께 따뜻하고 공감적인 응답을 해주세요.
"""
        
        return system_prompt + user_prompt + response_guidelines
    
    async def _generate_ai_response(self, prompt: str) -> Dict[str, Any]:
        """Generate AI response using LLM"""
        try:
            # In a real implementation, this would call AWS Bedrock
            # For now, we'll simulate the response
            
            # Simulate LLM call delay
            await self._simulate_llm_delay()
            
            # Generate simulated response based on prompt analysis
            response_content = self._generate_simulated_response(prompt)
            
            return {
                "content": response_content,
                "model_id": self.model_id,
                "token_usage": {
                    "input_tokens": len(prompt.split()),
                    "output_tokens": len(response_content.split()),
                    "total_tokens": len(prompt.split()) + len(response_content.split())
                }
            }
            
        except Exception as e:
            # Try fallback model
            try:
                response_content = self._generate_fallback_response()
                return {
                    "content": response_content,
                    "model_id": self.fallback_model_id,
                    "token_usage": {
                        "input_tokens": 0,
                        "output_tokens": len(response_content.split()),
                        "total_tokens": len(response_content.split())
                    }
                }
            except:
                raise Exception(f"Both primary and fallback LLM failed: {str(e)}")
    
    async def _simulate_llm_delay(self):
        """Simulate LLM processing delay"""
        import asyncio
        await asyncio.sleep(1.5)  # Simulate 1.5 second processing time
    
    def _generate_simulated_response(self, prompt: str) -> str:
        """Generate simulated response based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Analyze prompt content and generate appropriate response
        if "어린 시절" in prompt_lower or "어렸을 때" in prompt_lower:
            return "어린 시절의 소중한 추억을 들려주셔서 감사합니다. 그 시절이 정말 생생하게 전해집니다. 그때 가장 기억에 남는 순간은 어떤 것이었나요?"
        
        elif "가족" in prompt_lower or "부모" in prompt_lower:
            return "가족에 대한 따뜻한 마음이 느껴집니다. 가족과 함께한 소중한 시간들이 인생의 큰 보물이셨을 것 같아요. 가족과 함께한 특별한 순간이 또 있으시다면 들려주세요."
        
        elif "전쟁" in prompt_lower or "피난" in prompt_lower:
            return "그 어려운 시절을 겪으셨군요. 정말 힘든 시기였을 텐데 잘 견뎌내셨습니다. 그때의 경험이 지금의 강인함을 만들어주셨을 것 같아요. 그 시절 어떤 마음이셨는지 더 들려주실 수 있나요?"
        
        elif "직장" in prompt_lower or "일" in prompt_lower:
            return "오랜 직장 생활의 경험담을 들려주셔서 감사합니다. 그 시절의 열정과 노력이 느껴집니다. 일하시면서 가장 보람을 느꼈던 순간은 언제였나요?"
        
        else:
            return "소중한 이야기를 들려주셔서 감사합니다. 말씀해주신 내용이 정말 의미 깊게 다가옵니다. 그때의 기분이나 생각을 더 자세히 들려주실 수 있을까요?"
    
    def _generate_fallback_response(self) -> str:
        """Generate fallback response when LLM fails"""
        return "죄송합니다. 잠시 기술적인 문제가 있었습니다. 소중한 이야기를 들려주셔서 감사하고, 계속해서 대화를 나누고 싶습니다. 다시 한 번 말씀해 주시겠어요?"
    
    def _generate_follow_up_questions(
        self,
        user_message: str,
        user_profile: UserProfile,
        conversation_context: Dict[str, Any]
    ) -> list[str]:
        """Generate contextual follow-up questions"""
        message_lower = user_message.lower()
        
        # Base questions
        base_questions = [
            "그때 가장 기억에 남는 일은 무엇인가요?",
            "그 경험에서 배운 점이 있다면 무엇인가요?",
            "비슷한 다른 경험도 있으신가요?"
        ]
        
        # Context-specific questions
        if "가족" in message_lower:
            return [
                "가족과 함께한 가장 행복했던 순간은 언제인가요?",
                "가족에게서 배운 가장 소중한 가르침은 무엇인가요?",
                "후손들에게 전하고 싶은 가족의 이야기가 있나요?"
            ]
        
        elif "어린 시절" in message_lower:
            return [
                "어린 시절 가장 좋아했던 놀이는 무엇이었나요?",
                "그때 꿈꾸던 것이 있으시다면 무엇이었나요?",
                "어린 시절의 친구들과는 지금도 연락하시나요?"
            ]
        
        elif "전쟁" in message_lower or "피난" in message_lower:
            return [
                "그 시절 가장 힘들었던 순간은 언제였나요?",
                "어떻게 그 어려움을 극복하셨나요?",
                "그 경험이 지금의 삶에 어떤 영향을 주었나요?"
            ]
        
        elif "직장" in message_lower or "일" in message_lower:
            return [
                "직장에서 가장 기억에 남는 동료가 있으신가요?",
                "일하시면서 가장 큰 성취감을 느낀 때는 언제인가요?",
                "후배들에게 해주고 싶은 조언이 있다면?"
            ]
        
        return base_questions
