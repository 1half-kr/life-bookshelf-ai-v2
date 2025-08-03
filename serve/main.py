import os
from datetime import datetime

# 환경 변수를 가장 먼저 로드
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.development")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# AI 서버 라우터들 (환경 변수 로드 후 임포트)
from conversation.conversation_router_v2 import router as conversation_router
from autobiography.autobiography_router import router as autobiography_router

from logs import get_logger

logger = get_logger()


app = FastAPI(
    title="Life Bookshelf AI v2 - AI Processing Server",
    description="노년층 자서전 생성 시스템 AI 처리 서버",
    version="2.0.0",
    docs_url="/docs"
)

origins = [
    "http://localhost:8000",  # 백엔드 서버
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # 개발용
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI 서버 라우터들
app.include_router(conversation_router)
app.include_router(autobiography_router)


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Life Bookshelf AI v2 - AI Processing Server",
        "version": "2.0.0",
        "description": "노년층 자서전 생성 시스템 AI 처리 서버",
        "capabilities": [
            "실시간 대화 처리",
            "27개 챕터 분류",
            "AWS Bedrock 연동"
        ],
        "endpoints": {
            "conversation": "/conversation", 
            "autobiography": "/autobiography",
            "analysis": "/analysis",
            "monitoring": "/monitoring",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "ai_server": "running",
            "aws_bedrock": "connected",
            "backend_server_connection": "healthy"
        },
        "ai_models": {
            "claude_3_sonnet": "available",
            "claude_3_haiku": "available"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
