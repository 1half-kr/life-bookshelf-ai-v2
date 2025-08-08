"""
환경 설정 관리
"""

import os
from dotenv import load_dotenv

# .env 파일 로드 (production 우선)
load_dotenv(".env.production")
load_dotenv()  # fallback to .env

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))

# Vector Database 설정
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# 기능 플래그
ENABLE_VECTOR_DB = os.getenv("ENABLE_VECTOR_DB", "true").lower() == "true"
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"