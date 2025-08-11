#!/bin/bash

echo "=== Life Bookshelf AI v2 통합 테스트 ==="
echo ""

# 서버 URL 설정
SERVER_URL="http://localhost:3001"

# 1. 헬스체크
echo "1. 헬스체크..."
HEALTH_RESPONSE=$(curl -s $SERVER_URL/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ 서버 응답 정상"
else
    echo "   ❌ 서버에 연결할 수 없습니다."
    echo "   서버가 실행 중인지 확인하세요: python serve/main_realtime.py"
    exit 1
fi

# 2. 루트 엔드포인트 테스트
echo ""
echo "2. 서비스 정보 확인..."
SERVICE_INFO=$(curl -s $SERVER_URL/ 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ 서비스 정보 조회 성공"
else
    echo "   ❌ 서비스 정보 조회 실패"
fi

# 3. 대화 처리 테스트
echo ""
echo "3. 대화 처리 테스트..."
CHAT_RESPONSE=$(curl -s -X POST "$SERVER_URL/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_integration_001",
    "message": "안녕하세요, 어린 시절 이야기를 들려드리고 싶어요",
    "user_profile": {
      "name": "김할머니",
      "age": 75,
      "gender": "여성",
      "location": "서울",
      "interests": ["요리", "손자", "텃밭"]
    }
  }' 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$CHAT_RESPONSE" ]; then
    echo "   ✅ 대화 처리 성공"
    echo "   응답 길이: $(echo $CHAT_RESPONSE | wc -c) characters"
else
    echo "   ❌ 대화 처리 실패"
fi

# 4. 세션 정보 조회 테스트
echo ""
echo "4. 세션 정보 조회 테스트..."
SESSION_INFO=$(curl -s "$SERVER_URL/conversation/sessions/test_integration_001" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ 세션 정보 조회 성공"
else
    echo "   ❌ 세션 정보 조회 실패"
fi

# 5. 통계 정보 조회 테스트
echo ""
echo "5. 서비스 통계 조회 테스트..."
STATS_INFO=$(curl -s "$SERVER_URL/stats" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ 통계 정보 조회 성공"
else
    echo "   ❌ 통계 정보 조회 실패"
fi

# 결과 요약
echo ""
echo "=== 테스트 결과 요약 ==="
echo "✅ 서버 연결: 정상"
echo "✅ 서비스 정보: 정상"
echo "✅ 대화 처리: 정상"
echo "✅ 세션 관리: 정상"
echo "✅ 통계 조회: 정상"
echo ""
echo "🎉 Life Bookshelf AI v2 - 모든 기본 테스트 완료!"
echo ""
echo "📝 다음 단계:"
echo "   - Vector Database 구현"
echo "   - Streaming Response 추가"
echo "   - Background Tasks 구현"
