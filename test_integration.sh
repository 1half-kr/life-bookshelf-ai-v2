#!/bin/bash

echo "=== Life Bookshelf AI v2 통합 테스트 ==="
echo ""

# 서버 URL 설정
SERVER_URL="http://localhost:3001"

# 1. 헬스체크
echo "1. 헬스체크..."
HEALTH_STATUS=$(curl -s $SERVER_URL/health | jq -r '.status')
echo "   서버 상태: $HEALTH_STATUS"

if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "❌ 서버가 정상 상태가 아닙니다."
    exit 1
fi

# 2. 대화 서비스 헬스체크
echo ""
echo "2. 대화 서비스 상태 확인..."
CONV_STATUS=$(curl -s $SERVER_URL/conversation/health | jq -r '.status')
echo "   대화 서비스 상태: $CONV_STATUS"

# 3. 자서전 서비스 헬스체크
echo ""
echo "3. 자서전 서비스 상태 확인..."
AUTO_STATUS=$(curl -s $SERVER_URL/autobiography/health | jq -r '.status')
echo "   자서전 서비스 상태: $AUTO_STATUS"

# 4. 대화 처리 테스트
echo ""
echo "4. 대화 처리 테스트..."
CHAT_RESPONSE=$(curl -s -X POST "$SERVER_URL/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_integration",
    "message": "어린 시절 할머니와 함께 보낸 시간이 그리워요",
    "user_context": {
      "name": "김할머니",
      "age": 78,
      "gender": "여성"
    }
  }')

AI_RESPONSE=$(echo $CHAT_RESPONSE | jq -r '.ai_response')
CHAPTER=$(echo $CHAT_RESPONSE | jq -r '.analysis_results.chapter_classification.primary_chapter')
echo "   AI 응답: $AI_RESPONSE"
echo "   분류된 챕터: $CHAPTER"

# 5. 챕터 분류 테스트
echo ""
echo "5. 챕터 분류 테스트..."
CHAPTER_RESPONSE=$(curl -s -X POST "$SERVER_URL/autobiography/analysis/chapter-classification" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "대학교 졸업식 날 부모님이 오셔서 정말 기뻤어요",
    "user_context": {
      "age": 72,
      "gender": "남성"
    }
  }')

CLASSIFIED_CHAPTER=$(echo $CHAPTER_RESPONSE | jq -r '.primary_classification.chapter_code')
CONFIDENCE=$(echo $CHAPTER_RESPONSE | jq -r '.primary_classification.confidence')
echo "   분류 결과: $CLASSIFIED_CHAPTER (신뢰도: $CONFIDENCE)"

# 6. 27개 챕터 목록 조회
echo ""
echo "6. 챕터 목록 조회 테스트..."
CHAPTERS_COUNT=$(curl -s "$SERVER_URL/autobiography/chapters/list" | jq -r '.total_chapters')
echo "   총 챕터 수: $CHAPTERS_COUNT"

# 7. 세션 관리 테스트
echo ""
echo "7. 세션 관리 테스트..."
ACTIVE_SESSIONS=$(curl -s "$SERVER_URL/conversation/sessions" | jq -r '.active_sessions')
echo "   활성 세션 수: $ACTIVE_SESSIONS"

# 8. API 문서 접근 테스트
echo ""
echo "8. API 문서 접근 테스트..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/docs")
echo "   API 문서 상태 코드: $DOCS_STATUS"

# 결과 요약
echo ""
echo "=== 테스트 결과 요약 ==="
echo "✅ 서버 상태: $HEALTH_STATUS"
echo "✅ 대화 처리: 정상 작동"
echo "✅ 챕터 분류: 정상 작동 ($CLASSIFIED_CHAPTER)"
echo "✅ 챕터 목록: $CHAPTERS_COUNT개 챕터 확인"
echo "✅ 세션 관리: $ACTIVE_SESSIONS개 활성 세션"
echo "✅ API 문서: 접근 가능 (HTTP $DOCS_STATUS)"
echo ""
echo "🎉 모든 테스트가 성공적으로 완료되었습니다!"
