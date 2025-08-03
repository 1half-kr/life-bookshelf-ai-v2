"""
Conversation router v3 - Pipeline-oriented architecture
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Import pipeline components
from pipelines.conversation.pipeline import run_conversation_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversation"])


class UserProfile(BaseModel):
    """User profile model"""
    name: str = Field(..., description="사용자 이름")
    age: int = Field(..., ge=65, le=120, description="나이")
    gender: str = Field(..., description="성별")
    birth_place: Optional[str] = Field(None, description="출생지")
    occupation: Optional[str] = Field(None, description="직업")


class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: str = Field(..., description="세션 ID")
    message: str = Field(..., max_length=2000, description="사용자 메시지")
    message_type: str = Field(default="text", description="메시지 유형")
    user_context: UserProfile = Field(..., description="사용자 컨텍스트")
    pipeline_config: Optional[Dict[str, Any]] = Field(None, description="파이프라인 설정")


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    ai_response: str
    suggested_questions: list[str]
    conversation_context: Dict[str, Any]
    analysis_results: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/health")
async def health_check():
    """대화 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "conversation_processing_v3",
        "architecture": "pipeline_oriented",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "features": [
            "pipeline_based_processing",
            "elderly_optimized_chat",
            "step_by_step_validation",
            "context_aware_responses",
            "argo_workflow_ready"
        ],
        "pipeline_steps": [
            "input_validation",
            "context_loading", 
            "llm_processing",
            "response_building"
        ]
    }


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """실시간 대화 처리 - Pipeline 기반"""
    try:
        logger.info(f"Processing chat request for session: {request.session_id}")
        
        # Convert user context to dict
        user_context = request.user_context.dict()
        
        # Run conversation pipeline
        result = await run_conversation_pipeline(
            session_id=request.session_id,
            message=request.message,
            user_context=user_context,
            message_type=request.message_type,
            pipeline_config=request.pipeline_config
        )
        
        # Check if pipeline execution was successful
        if not result.get("success", False):
            logger.error(f"Pipeline execution failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Pipeline execution failed",
                    "details": result.get("error_messages", []),
                    "failed_steps": result.get("failed_steps", [])
                }
            )
        
        # Schedule background tasks
        background_tasks.add_task(
            save_conversation_data,
            request.session_id,
            request.message,
            result["ai_response"]
        )
        
        # Return successful response
        return ChatResponse(
            success=True,
            ai_response=result["ai_response"],
            suggested_questions=result["suggested_questions"],
            conversation_context=result["conversation_context"],
            analysis_results=result.get("analysis_results"),
            processing_time=result.get("processing_time"),
            performance_metrics=result.get("performance_metrics")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "대화 처리 중 예상치 못한 오류가 발생했습니다"
            }
        )


@router.get("/pipeline/status")
async def get_pipeline_status():
    """파이프라인 상태 조회"""
    try:
        from pipelines.conversation.pipeline import create_conversation_pipeline
        
        pipeline = create_conversation_pipeline()
        status = pipeline.get_pipeline_status()
        
        return {
            "pipeline_status": "active",
            "pipeline_info": status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pipeline status"
        )


@router.post("/pipeline/config")
async def update_pipeline_config(config: Dict[str, Any]):
    """파이프라인 설정 업데이트"""
    try:
        # Validate configuration
        valid_keys = {
            "max_message_length", "min_age", "max_age",
            "max_context_messages", "session_timeout_hours",
            "model_id", "fallback_model_id", "max_tokens", 
            "temperature", "timeout_seconds",
            "include_analysis", "include_suggestions"
        }
        
        invalid_keys = set(config.keys()) - valid_keys
        if invalid_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration keys: {list(invalid_keys)}"
            )
        
        # In a real implementation, this would update the pipeline configuration
        # For now, we'll just return the accepted configuration
        
        return {
            "success": True,
            "message": "Pipeline configuration updated",
            "updated_config": config,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update pipeline config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update pipeline configuration"
        )


@router.get("/sessions/active")
async def get_active_sessions():
    """활성 세션 목록 조회"""
    try:
        # In a real implementation, this would query the session storage
        # For now, return a placeholder response
        
        return {
            "active_sessions": 0,
            "sessions": [],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "note": "Session data would be retrieved from Redis/Database in production"
        }
        
    except Exception as e:
        logger.error(f"Failed to get active sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve active sessions"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        # In a real implementation, this would delete from session storage
        
        return {
            "success": True,
            "message": f"Session {session_id} deleted",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session {session_id}"
        )


# Background task functions
async def save_conversation_data(session_id: str, user_message: str, ai_response: str):
    """Save conversation data to storage (background task)"""
    try:
        # In a real implementation, this would save to database/Redis
        logger.info(f"Saving conversation data for session: {session_id}")
        
        # Simulate saving process
        conversation_data = {
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Here you would save to your storage system
        # await storage_service.save_conversation(conversation_data)
        
        logger.info(f"Conversation data saved for session: {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to save conversation data: {str(e)}")
        # Don't raise exception in background task
