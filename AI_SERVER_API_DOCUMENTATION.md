# 🤖 Life Bookshelf AI v2 - AI 서버 API 문서

## 🎯 시스템 개요
65세 이상 노년층을 위한 자서전 생성 시스템의 **AI 처리 및 실시간 응답** 담당 서버

**기본 URL**: `http://localhost:3000`  
**API 문서**: `http://localhost:3000/docs` (Swagger UI)  
**연동 백엔드 서버**: `http://localhost:8000`

---

## 🔍 1. 시스템 상태 API

### 1.1 AI 서버 상태 확인
```http
GET /health
```

**응답 예시**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-03T11:35:17.304240Z",
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
```

**설명**: 
- AI 서버의 전체 상태를 확인
- AWS Bedrock 연결 상태 확인
- 백엔드 서버와의 연동 상태 확인

### 1.2 메인 페이지
```http
GET /
```

**응답 예시**:
```json
{
  "message": "Life Bookshelf AI - AI Processing Server",
  "version": "2.0.0",
  "description": "노년층 자서전 생성 시스템 AI 처리 서버",
  "capabilities": [
    "실시간 대화 처리",
    "챕터 분류",
    "AWS Bedrock 연동"
  ]
}
```

---

## 💬 2. 실시간 대화 처리 API

### 2.1 대화 서비스 상태 확인
```http
GET /conversation/health
```

**응답 예시**:
```json
{
  "status": "healthy",
  "service": "conversation_processing",
  "timestamp": "2025-08-03T11:35:17Z",
  "features": [
    "elderly_optimized_chat",
    "chapter_classification",
    "context_awareness"
  ],
  "ai_models": {
    "primary": "claude-3-sonnet-20240229",
    "fallback": "claude-3-haiku-20240307",
    "status": "available"
  }
}
```

### 2.2 실시간 대화 처리
```http
POST /conversation/chat
Content-Type: application/json
```

**요청 본문**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "message": "어린 시절 6.25 전쟁 때 부산으로 피난을 갔었어요",
  "message_type": "text",
  "user_context": {
    "name": "김철수",
    "age": 75,
    "gender": "남성"
  },
  "conversation_settings": {
    "response_style": "empathetic",
    "follow_up_questions": true,
    "chapter_classification": true
  }
}
```

**파라미터 설명**:
- `session_id` (string, required): 대화 세션 ID
- `message` (string, required): 사용자 메시지 (최대 2000자)
- `message_type` (string, optional): 메시지 유형 ("text", "voice_transcribed")
- `user_context` (object, optional): 사용자 컨텍스트 정보
  - `name` (string): 사용자 이름
  - `age` (integer): 나이
  - `gender` (string): 성별
- `conversation_settings` (object, optional): 대화 설정
  - `response_style` (string): 응답 스타일 ("empathetic", "gentle", "encouraging")
  - `follow_up_questions` (boolean): 후속 질문 생성 여부
  - `chapter_classification` (boolean): 챕터 분류 수행 여부

**응답 예시**:
```json
{
  "success": true,
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "ai_response": "그 시절의 기억이 생생하게 전해집니다. 전쟁의 혼란 속에서도 가족과 함께 하셨다니, 정말 소중한 경험이셨을 것 같아요. 그때 기분은 어떠셨나요?",
  "processing_time": 2.8,
  "analysis_results": {
    "chapter_classification": {
      "primary_chapter": "society_country",
      "confidence": 0.85,
      "alternative_chapters": [
        {"chapter": "growth_childhood", "confidence": 0.72}
      ]
    },
    "memory_classification": {
      "memory_type": "historical_personal_experience",
      "importance_score": 0.9,
      "life_stage": "childhood",
      "autobiography_relevance": "high"
    }
  },
  "suggested_questions": [
    "그때 가장 기억에 남는 일은 무엇인가요?",
    "피난 생활에서 어려웠던 점은 무엇이었나요?",
    "그 경험이 인생에 어떤 영향을 주었나요?"
  ],
  "conversation_context": {
    "topic_continuity": "war_experience",
    "suggested_next_topics": ["family_during_war", "post_war_life"]
  }
}
```

**오류 응답**:
```json
{
  "success": false,
  "error": "AI 모델 응답 생성에 실패했습니다",
  "error_code": "AI_MODEL_UNAVAILABLE",
  "timestamp": "2025-08-03T11:35:17Z",
  "details": {
    "model_id": "claude-3-sonnet-20240229",
    "retry_available": true,
    "fallback_model": "claude-3-haiku-20240307"
  }
}
```

### 2.3 대화 컨텍스트 업데이트
```http
PUT /conversation/context/{session_id}
Content-Type: application/json
```

**요청 본문**:
```json
{
  "user_profile_updates": {
    "preferred_topics": ["family", "childhood"],
    "conversation_pace": "slow"
  },
  "conversation_history_summary": "사용자가 전쟁 시절 피난 경험에 대해 이야기하고 있음"
}
```

**파라미터 설명**:
- `user_profile_updates` (object, optional): 사용자 프로필 업데이트
  - `preferred_topics` (array): 선호 주제 목록
  - `conversation_pace` (string): 대화 속도 ("slow", "normal", "fast")
- `conversation_history_summary` (string, optional): 대화 히스토리 요약

**응답 예시**:
```json
{
  "success": true,
  "context_updated": true,
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "updated_at": "2025-08-03T12:45:30Z"
}
```

---

## 🧠 3. AI 분석 API

### 3.1 챕터 분류
```http
POST /analysis/chapter-classification
Content-Type: application/json
```

**요청 본문**:
```json
{
  "text": "대학교 1학년 때 처음 만난 친구들과의 추억이 아직도 생생해요",
  "user_context": {
    "age": 73,
    "gender": "남성"
  },
  "classification_mode": "detailed"
}
```

**파라미터 설명**:
- `text` (string, required): 분류할 텍스트 (최대 1000자)
- `user_context` (object, optional): 사용자 컨텍스트
  - `age` (integer): 나이
  - `gender` (string): 성별
- `classification_mode` (string, optional): 분류 모드 ("basic", "detailed")

**응답 예시**:
```json
{
  "success": true,
  "primary_classification": {
    "major_category": "학창시절",
    "minor_category": "친구",
    "chapter_code": "school_friends",
    "confidence": 0.92
  },
  "alternative_classifications": [
    {
      "major_category": "인생 경험",
      "minor_category": "사건",
      "chapter_code": "life_events",
      "confidence": 0.78
    }
  ],
  "classification_reasoning": {
    "key_indicators": ["대학교", "친구들", "추억"],
    "life_stage_markers": ["1학년", "처음 만난"],
    "emotional_markers": ["생생해요"]
  },
  "autobiography_suggestions": {
    "chapter_placement": "학창시절 - 대학 생활",
    "narrative_style": "friendship_focused",
    "follow_up_topics": ["대학 생활", "평생 친구", "청춘 시절"]
  },
  "processing_time": 0.8
}
```

---

## 🔄 4. 백엔드 연동 API

### 4.1 대화 데이터 백엔드 전송
```http
POST /backend/save-conversation
Content-Type: application/json
```

**요청 본문**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "conversation_data": {
    "user_message": "어린 시절 6.25 전쟁 때 부산으로 피난을 갔었어요",
    "ai_response": "그 시절의 기억이 생생하게 전해집니다...",
    "timestamp": "2025-08-03T12:30:45Z",
    "analysis_results": {
      "chapter_classification": {
        "primary_chapter": "society_country",
        "confidence": 0.85
      },
      "memory_classification": {
        "memory_type": "historical_personal_experience",
        "importance_score": 0.9
      }
    }
  }
}
```

**파라미터 설명**:
- `session_id` (string, required): 세션 ID
- `conversation_data` (object, required): 대화 데이터
  - `user_message` (string): 사용자 메시지
  - `ai_response` (string): AI 응답
  - `timestamp` (string): 타임스탬프 (ISO 8601)
  - `analysis_results` (object): 분석 결과

**응답 예시**:
```json
{
  "success": true,
  "backend_response": "data_saved",
  "conversation_id": "conv_abc123",
  "saved_at": "2025-08-03T12:30:46Z"
}
```

### 4.2 세션 상태 동기화
```http
POST /backend/sync-session
Content-Type: application/json
```

**요청 본문**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "session_updates": {
    "last_activity": "2025-08-03T12:45:30Z",
    "message_count": 15,
    "current_topic": "war_experience"
  }
}
```

**응답 예시**:
```json
{
  "success": true,
  "sync_status": "completed",
  "updated_at": "2025-08-03T12:45:31Z"
}
```

---

## 📊 5. AI 성능 모니터링 API

### 5.1 AI 처리 성능 조회
```http
GET /monitoring/ai-performance
```

**응답 예시**:
```json
{
  "current_performance": {
    "average_response_time": 2.3,
    "success_rate": 99.2,
    "active_sessions": 45,
    "queue_length": 3
  },
  "model_performance": {
    "claude_3_sonnet": {
      "response_time": 2.8,
      "success_rate": 99.5,
      "usage_percentage": 75
    },
    "claude_3_haiku": {
      "response_time": 1.1,
      "success_rate": 98.8,
      "usage_percentage": 25
    }
  },
  "resource_usage": {
    "cpu_usage": 65,
    "memory_usage": 78,
    "gpu_usage": 45
  },
  "daily_statistics": {
    "total_conversations": 1250,
    "total_messages": 8900,
    "average_session_duration": "42분"
  }
}
```

**Query Parameters**:
- `period` (string, optional): 조회 기간 ("hour", "day", "week")
- `detailed` (boolean, optional): 상세 정보 포함 여부

---

## 🚨 6. 오류 처리

### 6.1 일반적인 HTTP 상태 코드

- **200 OK**: 요청 성공
- **400 Bad Request**: 잘못된 요청 형식
- **401 Unauthorized**: 인증 필요
- **404 Not Found**: 리소스를 찾을 수 없음
- **429 Too Many Requests**: 요청 한도 초과
- **500 Internal Server Error**: 서버 내부 오류
- **503 Service Unavailable**: 서비스 일시 불가

### 6.2 AI 서버 특화 오류 코드

- `AI_MODEL_UNAVAILABLE`: AI 모델 서비스 불가
- `CHAPTER_CLASSIFICATION_FAILED`: 챕터 분류 실패
- `AWS_SERVICE_ERROR`: AWS 서비스 오류
- `CONTEXT_PROCESSING_ERROR`: 컨텍스트 처리 오류
- `BACKEND_SYNC_FAILED`: 백엔드 동기화 실패
- `SESSION_NOT_FOUND`: 세션을 찾을 수 없음
- `MESSAGE_TOO_LONG`: 메시지 길이 초과
- `RATE_LIMIT_EXCEEDED`: 요청 한도 초과

### 6.3 오류 응답 형식
```json
{
  "success": false,
  "error": "AI 모델 응답 생성에 실패했습니다",
  "error_code": "AI_MODEL_UNAVAILABLE",
  "timestamp": "2025-08-03T11:35:17Z",
  "details": {
    "model_id": "claude-3-sonnet-20240229",
    "retry_available": true,
    "fallback_model": "claude-3-haiku-20240307"
  },
  "suggested_action": "잠시 후 다시 시도하거나 고객 지원에 문의하세요"
}
```

---

## 🔐 7. 인증 및 보안

### 7.1 내부 서비스 인증
```http
X-Service-Token: internal_service_token_here
```

### 7.2 세션 기반 인증
```http
X-Session-ID: session_id_here
```

### 7.3 보안 고려사항
- IAM 역할 기반 AWS 서비스 접근
- API 요청 로깅 및 모니터링
- 개인정보 처리 최소화
- 세션 데이터 암호화

---

## 📝 8. 사용 예시

### 8.1 기본 대화 플로우
```bash
# 1. 대화 처리
curl -X POST "http://localhost:3000/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_12345",
    "message": "어린 시절 이야기를 들려드리고 싶어요",
    "message_type": "text",
    "user_context": {
      "name": "김철수",
      "age": 75,
      "gender": "남성"
    }
  }'

# 2. 응답 예시
{
  "success": true,
  "ai_response": "어떤 어린 시절 이야기를 들려주실까요?",
  "analysis_results": {
    "chapter_classification": {
      "primary_chapter": "growth_childhood",
      "confidence": 0.88
    }
  }
}
```

### 8.2 챕터 분류 API 활용
```bash
# 챕터 분류
curl -X POST "http://localhost:3000/analysis/chapter-classification" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "대학교 때 친구들과의 추억",
    "user_context": {"age": 73, "gender": "남성"},
    "classification_mode": "detailed"
  }'

# 응답 예시
{
  "success": true,
  "primary_classification": {
    "major_category": "학창시절",
    "minor_category": "친구",
    "chapter_code": "school_friends",
    "confidence": 0.92
  }
}
```

---

## 🎯 9. 성능 및 제한사항

### 9.1 응답 시간 목표
- 기본 대화 처리: < 3초
- 챕터 분류: < 1초
- 성능 모니터링: < 500ms

### 9.2 사용 제한
- 동시 대화 세션: 최대 100개
- 텍스트 길이: 메시지당 최대 2000자
- API 호출: 분당 최대 200회 (세션당)
- 챕터 분류: 텍스트당 최대 1000자

### 9.3 지원 사양
- 언어: 한국어 (주), 영어 (부분 지원)
- AI 모델: Claude 3 Sonnet, Claude 3 Haiku
- AWS 리전: ap-northeast-2 (서울)
- 동시 처리: 최대 100개 세션

이 AI 서버 API 문서를 통해 Life Bookshelf AI v2의 실시간 AI 처리 기능을 효과적으로 활용할 수 있습니다.
