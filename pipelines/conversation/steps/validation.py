"""
Input validation step for conversation pipeline
"""
import re
from typing import Dict, Any

from shared.models.pipeline import PipelineStep, StepContext, StepResult, StepStatus
from shared.models.data import UserProfile, MessageType


class InputValidationStep(PipelineStep):
    """Validates user input and session data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("input_validation", config)
        self.max_message_length = self.get_config("max_message_length", 2000)
        self.min_age = self.get_config("min_age", 65)
        self.max_age = self.get_config("max_age", 120)
    
    async def validate_input(self, context: StepContext) -> bool:
        """Validate that required input fields are present"""
        required_fields = ["session_id", "message", "user_context"]
        return all(field in context.input_data for field in required_fields)
    
    async def execute(self, context: StepContext) -> StepResult:
        """Execute input validation"""
        try:
            input_data = context.input_data
            
            # Validate session ID
            session_id = input_data.get("session_id", "").strip()
            if not session_id:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message="Session ID is required"
                )
            
            if len(session_id) > 100:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message="Session ID too long (max 100 characters)"
                )
            
            # Validate message content
            message = input_data.get("message", "").strip()
            if not message:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message="Message content is required"
                )
            
            if len(message) > self.max_message_length:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message=f"Message too long (max {self.max_message_length} characters)"
                )
            
            # Check for inappropriate content
            if self._contains_inappropriate_content(message):
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message="Message contains inappropriate content"
                )
            
            # Validate user context
            user_context = input_data.get("user_context", {})
            validation_result = self._validate_user_profile(user_context)
            if not validation_result["valid"]:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message=validation_result["error"]
                )
            
            # Validate message type
            message_type = input_data.get("message_type", "text")
            if message_type not in [mt.value for mt in MessageType]:
                return StepResult(
                    step_name=self.name,
                    status=StepStatus.FAILED,
                    error_message=f"Invalid message type: {message_type}"
                )
            
            # Create validated user profile
            user_profile = UserProfile(
                name=user_context["name"],
                age=user_context["age"],
                gender=user_context["gender"],
                birth_place=user_context.get("birth_place"),
                occupation=user_context.get("occupation")
            )
            
            # Return validated data
            return StepResult(
                step_name=self.name,
                status=StepStatus.COMPLETED,
                output_data={
                    "validated_session_id": session_id,
                    "validated_message": message,
                    "validated_message_type": MessageType(message_type),
                    "validated_user_profile": user_profile,
                    "message_word_count": len(message.split()),
                    "message_char_count": len(message)
                },
                metadata={
                    "validation_rules_applied": [
                        "session_id_length",
                        "message_length", 
                        "content_appropriateness",
                        "user_profile_completeness",
                        "age_range"
                    ]
                }
            )
            
        except Exception as e:
            return StepResult(
                step_name=self.name,
                status=StepStatus.FAILED,
                error_message=f"Validation error: {str(e)}"
            )
    
    def _validate_user_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user profile data"""
        # Check required fields
        required_fields = ["name", "age", "gender"]
        for field in required_fields:
            if field not in user_context or not user_context[field]:
                return {
                    "valid": False,
                    "error": f"User {field} is required"
                }
        
        # Validate name
        name = user_context["name"].strip()
        if len(name) < 2 or len(name) > 50:
            return {
                "valid": False,
                "error": "User name must be between 2 and 50 characters"
            }
        
        # Validate age
        try:
            age = int(user_context["age"])
            if not (self.min_age <= age <= self.max_age):
                return {
                    "valid": False,
                    "error": f"Age must be between {self.min_age} and {self.max_age}"
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": "Age must be a valid number"
            }
        
        # Validate gender
        valid_genders = ["남성", "여성", "기타"]
        if user_context["gender"] not in valid_genders:
            return {
                "valid": False,
                "error": f"Gender must be one of: {', '.join(valid_genders)}"
            }
        
        return {"valid": True}
    
    def _contains_inappropriate_content(self, message: str) -> bool:
        """Check for inappropriate content in message"""
        # Simple inappropriate content detection
        inappropriate_patterns = [
            r'욕설|비속어|혐오',  # 욕설, 비속어, 혐오 표현
            r'개인정보|주민번호|전화번호',  # 개인정보
            r'광고|홍보|스팸'  # 광고성 내용
        ]
        
        message_lower = message.lower()
        for pattern in inappropriate_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
