"""
Main FastAPI application with Pipeline-oriented architecture
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from project root
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env.development")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import pipeline-based routers
from conversation.conversation_router_v3 import router as conversation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Life Bookshelf AI v2 - Pipeline Architecture",
    description="노년층 자서전 생성 시스템 - Pipeline-oriented Architecture",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = [
    "http://localhost:8000",  # Backend server
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # Development
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "서버에서 예상치 못한 오류가 발생했습니다",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Register routers
app.include_router(conversation_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """전체 시스템 상태 확인"""
    return {
        "status": "healthy",
        "service": "life_bookshelf_ai_v2_pipeline",
        "architecture": "pipeline_oriented",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "features": [
            "pipeline_based_processing",
            "argo_workflow_integration",
            "elderly_optimized_conversation",
            "step_by_step_validation",
            "context_aware_responses",
            "background_task_processing"
        ],
        "available_pipelines": [
            "conversation_processing",
            "analysis_processing",
            "autobiography_generation"
        ],
        "environment": {
            "python_version": sys.version,
            "fastapi_version": "0.104.1",
            "pipeline_architecture": "enabled"
        }
    }

# System information endpoint
@app.get("/system/info")
async def system_info():
    """시스템 정보 조회"""
    return {
        "system": {
            "architecture": "Pipeline-oriented",
            "processing_model": "Step-by-step pipeline execution",
            "scalability": "Horizontal scaling with Argo Workflows",
            "fault_tolerance": "Step-level error handling and recovery"
        },
        "pipelines": {
            "conversation": {
                "steps": ["validation", "context_loading", "llm_processing", "response_building"],
                "average_latency": "2-3 seconds",
                "throughput": "100+ requests/minute"
            },
            "analysis": {
                "steps": ["preprocessing", "chapter_classification", "emotion_analysis", "memory_scoring"],
                "average_latency": "1-2 seconds",
                "throughput": "200+ requests/minute"
            }
        },
        "infrastructure": {
            "container_orchestration": "Kubernetes",
            "workflow_engine": "Argo Workflows",
            "message_broker": "Redis/Kafka",
            "storage": "Redis + PostgreSQL",
            "monitoring": "Prometheus + Grafana"
        }
    }

# Pipeline management endpoints
@app.get("/pipelines")
async def list_pipelines():
    """사용 가능한 파이프라인 목록"""
    return {
        "pipelines": [
            {
                "name": "conversation_processing",
                "description": "노년층 특화 대화 처리 파이프라인",
                "steps": 4,
                "average_duration": "2-3 seconds",
                "status": "active"
            },
            {
                "name": "analysis_processing", 
                "description": "메시지 분석 파이프라인",
                "steps": 4,
                "average_duration": "1-2 seconds",
                "status": "development"
            },
            {
                "name": "autobiography_generation",
                "description": "자서전 생성 파이프라인",
                "steps": 4,
                "average_duration": "10-30 seconds",
                "status": "development"
            }
        ],
        "total_pipelines": 3,
        "active_pipelines": 1
    }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """시스템 메트릭 조회"""
    return {
        "pipeline_metrics": {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "current_active_pipelines": 0
        },
        "resource_usage": {
            "cpu_usage": "N/A",
            "memory_usage": "N/A",
            "gpu_usage": "N/A"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "note": "Metrics would be collected from Prometheus in production"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Life Bookshelf AI v2 Pipeline Server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("Pipeline-oriented architecture enabled")
    
    uvicorn.run(
        "main_pipeline:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )
