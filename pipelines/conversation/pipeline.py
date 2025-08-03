"""
Main conversation processing pipeline
"""
from typing import Dict, Any, Optional

from shared.models.pipeline import Pipeline
from .steps.validation import InputValidationStep
from .steps.context_loader import ContextLoaderStep
from .steps.llm_processor import LLMProcessorStep
from .steps.response_builder import ResponseBuilderStep


class ConversationPipeline(Pipeline):
    """Complete conversation processing pipeline"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("conversation_processing", config)
        self.build_pipeline()
    
    def build_pipeline(self) -> None:
        """Build the conversation processing pipeline"""
        # Step 1: Input Validation
        validation_config = {
            "max_message_length": self.config.get("max_message_length", 2000),
            "min_age": self.config.get("min_age", 65),
            "max_age": self.config.get("max_age", 120)
        }
        self.add_step(InputValidationStep(validation_config))
        
        # Step 2: Context Loading
        context_config = {
            "max_context_messages": self.config.get("max_context_messages", 10),
            "session_timeout_hours": self.config.get("session_timeout_hours", 2)
        }
        self.add_step(ContextLoaderStep(context_config))
        
        # Step 3: LLM Processing
        llm_config = {
            "model_id": self.config.get("model_id", "claude-3-sonnet-20240229"),
            "fallback_model_id": self.config.get("fallback_model_id", "claude-3-haiku-20240307"),
            "max_tokens": self.config.get("max_tokens", 1000),
            "temperature": self.config.get("temperature", 0.7),
            "timeout_seconds": self.config.get("timeout_seconds", 30)
        }
        self.add_step(LLMProcessorStep(llm_config))
        
        # Step 4: Response Building
        response_config = {
            "include_analysis": self.config.get("include_analysis", True),
            "include_suggestions": self.config.get("include_suggestions", True)
        }
        self.add_step(ResponseBuilderStep(response_config))
    
    async def process_conversation(
        self,
        session_id: str,
        message: str,
        user_context: Dict[str, Any],
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Process a conversation message through the pipeline"""
        
        input_data = {
            "session_id": session_id,
            "message": message,
            "user_context": user_context,
            "message_type": message_type
        }
        
        # Execute the pipeline
        result = await self.execute(input_data)
        
        if result.is_successful:
            # Extract the final response from the last step
            final_response = None
            for step_result in reversed(result.step_results):
                if step_result.step_name == "response_builder" and step_result.is_successful:
                    final_response = step_result.output_data.get("final_response")
                    break
            
            if final_response:
                return final_response
            else:
                return {
                    "success": False,
                    "error": "Failed to build final response",
                    "pipeline_result": result
                }
        else:
            # Return error information
            failed_steps = result.failed_steps
            error_messages = [step.error_message for step in failed_steps if step.error_message]
            
            return {
                "success": False,
                "error": "Pipeline execution failed",
                "failed_steps": [step.step_name for step in failed_steps],
                "error_messages": error_messages,
                "pipeline_result": result
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline configuration and status"""
        return {
            "pipeline_name": self.name,
            "pipeline_id": self.pipeline_id,
            "step_count": len(self.steps),
            "steps": [
                {
                    "name": step.name,
                    "config": step.config
                }
                for step in self.steps
            ],
            "configuration": self.config
        }


# Pipeline factory function
def create_conversation_pipeline(config: Optional[Dict[str, Any]] = None) -> ConversationPipeline:
    """Factory function to create a conversation pipeline"""
    default_config = {
        # Validation settings
        "max_message_length": 2000,
        "min_age": 65,
        "max_age": 120,
        
        # Context settings
        "max_context_messages": 10,
        "session_timeout_hours": 2,
        
        # LLM settings
        "model_id": "claude-3-sonnet-20240229",
        "fallback_model_id": "claude-3-haiku-20240307",
        "max_tokens": 1000,
        "temperature": 0.7,
        "timeout_seconds": 30,
        
        # Response settings
        "include_analysis": True,
        "include_suggestions": True
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    return ConversationPipeline(default_config)


# Async pipeline runner for external use
async def run_conversation_pipeline(
    session_id: str,
    message: str,
    user_context: Dict[str, Any],
    message_type: str = "text",
    pipeline_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Run conversation pipeline with given parameters"""
    
    pipeline = create_conversation_pipeline(pipeline_config)
    
    return await pipeline.process_conversation(
        session_id=session_id,
        message=message,
        user_context=user_context,
        message_type=message_type
    )
