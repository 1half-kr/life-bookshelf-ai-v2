#!/bin/bash

echo "🚀 Life Bookshelf AI v2 - 서비스 시작"
echo "=================================="

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# 가상환경 활성화
echo "📦 가상환경 활성화..."
source .venv/bin/activate

# 환경 변수 로드
if [ -f .env.development ]; then
    echo "🔧 환경 변수 로드..."
    export $(cat .env.development | grep -v '^#' | xargs)
fi

# FastAPI 서버 시작
echo "🌟 FastAPI 서버 시작..."
echo "서버 주소: http://localhost:3000"
echo "API 문서: http://localhost:3000/docs"
echo "=================================="
cd serve
python main_realtime.py
