"""
환경 설정 관리
"""

import os
from dotenv import load_dotenv

# .env 파일 로드 (production 우선)
load_dotenv(".env.production")
load_dotenv()  # fallback to .env

class Config:
    """애플리케이션 설정 클래스"""
    
    # 서버 설정
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "3000"))
    
    # Vector Database 설정
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # 기능 플래그
    ENABLE_VECTOR_DB = os.getenv("ENABLE_VECTOR_DB", "true").lower() == "true"
    ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"

# 하위 호환성을 위한 전역 변수들
HOST = Config.HOST
PORT = Config.PORT
CHROMA_PERSIST_DIRECTORY = Config.CHROMA_PERSIST_DIRECTORY
ENABLE_VECTOR_DB = Config.ENABLE_VECTOR_DB
ENABLE_STREAMING = Config.ENABLE_STREAMING