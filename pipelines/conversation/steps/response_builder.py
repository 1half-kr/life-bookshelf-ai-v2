"""
Response building step for conversation pipeline
"""
from typing import Dict, Any
import uuid
from datetime import datetime

from shared.models.pipeline import PipelineStep, StepContext, StepResult, StepStatus
from shared.models.data import Message, MessageType, ConversationSession


class ResponseBuilderStep(PipelineStep):
    """Builds final response with all analysis results"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("response_builder", config)
        self.include_analysis = self.get_config("include_analysis", True)
        self.include_suggestions = self.get_config("include_suggestions", True)
    
    async def execute(self, context: StepContext) -> StepResult:
        """Execute response building"""
        try:
            # Extract all pipeline data
            session = context.input_data["conversation_session"]
            user_message = context.input_data["validated_message"]
            user_profile = context.input_data["validated_user_profile"]
            ai_response = context.input_data["ai_response"]
            follow_up_questions = context.input_data["follow_up_questions"]
            
            # Get analysis results if available
            chapter_classification = context.input_data.get("chapter_classification")
            emotion_analysis = context.input_data.get("emotion_analysis")
            memory_importance = context.input_data.get("memory_importance")
            
            # Create user message object
            user_message_obj = Message(
                id=str(uuid.uuid4()),
                content=user_message,
                message_type=context.input_data["validated_message_type"],
                sender="user",
                timestamp=datetime.utcnow()
            )
            
            # Create AI response message object
            ai_message_obj = Message(
                id=str(uuid.uuid4()),
                content=ai_response,
                message_type=MessageType.TEXT,
                sender="ai",
                timestamp=datetime.utcnow(),
                metadata={
                    "model_used": context.input_data.get("model_used"),
                    "token_usage": context.input_data.get("token_usage"),
                    "chapter_classification": chapter_classification,
                    "emotion_analysis": emotion_analysis,
                    "memory_importance": memory_importance
                }
            )
            
            # Update conversation session
            session.add_message(user_message_obj)
            session.add_message(ai_message_obj)
            
            # Build conversation context for next interaction
            conversation_context = self._build_conversation_context(session)
            
            # Build final response
            final_response = self._build_final_response(
                ai_response=ai_response,
                follow_up_questions=follow_up_questions,
                chapter_classification=chapter_classification,
                emotion_analysis=emotion_analysis,
                memory_importance=memory_importance,
                conversation_context=conversation_context,
                processing_metrics=self._extract_processing_metrics(context)
            )
            
            return StepResult(
                step_name=self.name,
                status=StepStatus.COMPLETED,
                output_data={
                    "final_response": final_response,
                    "updated_session": session,
                    "user_message_obj": user_message_obj,
                    "ai_message_obj": ai_message_obj
                },
                metadata={
                    "response_components": list(final_response.keys()),
                    "session_message_count": len(session.messages),
                    "conversation_duration": session.conversation_duration
                }
            )
            
        except Exception as e:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error_message=f"Response building error: {str(e)}"
            )
    
    def _build_conversation_context(self, session: ConversationSession) -> Dict[str, Any]:
        """Build conversation context for response"""
        recent_messages = session.messages[-5:] if len(session.messages) > 5 else session.messages
        
        # Extract topics from recent conversation
        topics = self._extract_topics_from_messages(recent_messages)
        
        return {
            "topic_continuity": topics[-1] if topics else "general",
            "suggested_next_topics": self._suggest_next_topics(topics),
            "conversation_flow": self._analyze_conversation_flow(recent_messages),
            "engagement_level": self._calculate_engagement_level(session)
        }
    
    def _build_final_response(
        self,
        ai_response: str,
        follow_up_questions: list[str],
        chapter_classification: Dict[str, Any] = None,
        emotion_analysis: Dict[str, Any] = None,
        memory_importance: Dict[str, Any] = None,
        conversation_context: Dict[str, Any] = None,
        processing_metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Build the final response structure"""
        response = {
            "success": True,
            "ai_response": ai_response,
            "suggested_questions": follow_up_questions,
            "conversation_context": conversation_context or {}
        }
        
        # Add analysis results if available and enabled
        if self.include_analysis:
            analysis_results = {}
            
            if chapter_classification:
                analysis_results["chapter_classification"] = chapter_classification
            
            if emotion_analysis:
                analysis_results["emotion_analysis"] = emotion_analysis
            
            if memory_importance:
                analysis_results["memory_classification"] = memory_importance
            
            if analysis_results:
                response["analysis_results"] = analysis_results
        
        # Add processing metrics
        if processing_metrics:
            response["processing_time"] = processing_metrics.get("total_time", 0.0)
            response["performance_metrics"] = {
                "validation_time": processing_metrics.get("validation_time", 0.0),
                "context_loading_time": processing_metrics.get("context_loading_time", 0.0),
                "llm_processing_time": processing_metrics.get("llm_processing_time", 0.0),
                "analysis_time": processing_metrics.get("analysis_time", 0.0)
            }
        
        return response
    
    def _extract_processing_metrics(self, context: StepContext) -> Dict[str, Any]:
        """Extract processing metrics from pipeline context"""
        metrics = {}
        
        # Get timing information from context metadata
        if hasattr(context, 'metadata'):
            for key, value in context.metadata.items():
                if key.endswith('_time'):
                    metrics[key] = value
        
        # Calculate total time from input data
        step_times = [
            context.input_data.get("validation_time", 0.0),
            context.input_data.get("context_loading_time", 0.0),
            context.input_data.get("llm_processing_time", 0.0),
            context.input_data.get("analysis_time", 0.0)
        ]
        
        metrics["total_time"] = sum(step_times)
        
        return metrics
    
    def _extract_topics_from_messages(self, messages: list[Message]) -> list[str]:
        """Extract topics from recent messages"""
        topics = []
        
        topic_keywords = {
            "family": ["가족", "부모", "아버지", "어머니", "형제", "자매"],
            "childhood": ["어린 시절", "어렸을 때", "유년기", "놀이"],
            "school": ["학교", "공부", "선생님", "친구", "교실"],
            "work": ["직장", "일", "회사", "직업", "근무"],
            "war": ["전쟁", "피난", "6.25", "부산"],
            "marriage": ["결혼", "신랑", "신부", "혼례", "배우자"],
            "health": ["건강", "병원", "의사", "치료"]
        }
        
        for message in messages:
            if message.is_from_user:
                content = message.content.lower()
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        if topic not in topics:
                            topics.append(topic)
        
        return topics
    
    def _suggest_next_topics(self, current_topics: list[str]) -> list[str]:
        """Suggest next conversation topics based on current topics"""
        topic_transitions = {
            "family": ["childhood", "marriage", "work"],
            "childhood": ["school", "family", "friends"],
            "school": ["work", "friends", "hobbies"],
            "work": ["family", "retirement", "achievements"],
            "war": ["family", "childhood", "resilience"],
            "marriage": ["family", "children", "home"],
            "health": ["family", "lifestyle", "wisdom"]
        }
        
        suggestions = []
        for topic in current_topics:
            if topic in topic_transitions:
                suggestions.extend(topic_transitions[topic])
        
        # Remove duplicates and current topics
        suggestions = list(set(suggestions) - set(current_topics))
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _analyze_conversation_flow(self, messages: list[Message]) -> str:
        """Analyze the flow of conversation"""
        if len(messages) < 2:
            return "beginning"
        
        user_messages = [msg for msg in messages if msg.is_from_user]
        
        if len(user_messages) <= 2:
            return "warming_up"
        elif len(user_messages) <= 5:
            return "engaging"
        else:
            return "deep_conversation"
    
    def _calculate_engagement_level(self, session: ConversationSession) -> str:
        """Calculate user engagement level"""
        user_messages = [msg for msg in session.messages if msg.is_from_user]
        
        if not user_messages:
            return "low"
        
        # Calculate average message length
        avg_length = sum(msg.word_count for msg in user_messages) / len(user_messages)
        
        # Calculate conversation frequency
        if len(user_messages) >= 10 and avg_length >= 15:
            return "high"
        elif len(user_messages) >= 5 and avg_length >= 8:
            return "medium"
        else:
            return "low"
