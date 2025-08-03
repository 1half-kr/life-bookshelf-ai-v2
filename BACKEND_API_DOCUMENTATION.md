# 🗄️ Life Bookshelf AI v2 - 백엔드 서버 API 문서

## 🎯 시스템 개요
65세 이상 노년층을 위한 자서전 생성 시스템의 **데이터 관리 및 비즈니스 로직** 담당 서버

**기본 URL**: `http://localhost:8000`  
**API 문서**: `http://localhost:8000/docs` (Swagger UI)  
**연동 AI 서버**: `http://localhost:3000`

---

## 🔍 1. 시스템 상태 API

### 1.1 백엔드 서버 상태 확인
```http
GET /health
```

**응답 예시**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-03T11:35:17.304240Z",
  "services": {
    "backend_server": "running",
    "database": "connected",
    "file_storage": "available",
    "ai_server_connection": "healthy"
  },
  "database_info": {
    "type": "PostgreSQL",
    "connection_pool": "active",
    "migrations": "up_to_date"
  }
}
```

**설명**: 
- 백엔드 서버의 전체 상태를 확인
- 데이터베이스 연결 상태 확인
- AI 서버와의 연동 상태 확인

### 1.2 메인 페이지
```http
GET /
```

**응답 예시**:
```json
{
  "message": "Life Bookshelf AI - Backend Server",
  "version": "2.0.0",
  "description": "노년층 자서전 생성 시스템 백엔드 서버",
  "responsibilities": [
    "사용자 데이터 관리",
    "세션 관리",
    "자서전 생성 작업 관리",
    "파일 저장소 관리",
    "통계 및 분석"
  ]
}
```

---

## 👤 2. 사용자 관리 API

### 2.1 사용자 프로필 생성
```http
POST /users/profile
Content-Type: application/json
```

**요청 본문**:
```json
{
  "name": "김철수",
  "age": 75,
  "gender": "남성",
  "birth_place": "서울",
  "occupation": "교사",
  "family_info": "2남 1녀의 아버지",
  "contact_info": {
    "phone": "010-1234-5678",
    "email": "kim@example.com"
  }
}
```

**파라미터 설명**:
- `name` (string, required): 사용자 이름 (최대 50자)
- `age` (integer, required): 나이 (65-120)
- `gender` (string, required): 성별 ("남성", "여성")
- `birth_place` (string, optional): 출생지 (최대 100자)
- `occupation` (string, optional): 직업 (최대 100자)
- `family_info` (string, optional): 가족 정보 (최대 200자)
- `contact_info` (object, optional): 연락처 정보
  - `phone` (string): 전화번호
  - `email` (string): 이메일 주소

**응답 예시**:
```json
{
  "user_id": "user_12345",
  "profile_created": true,
  "created_at": "2025-08-03T11:35:17Z",
  "message": "사용자 프로필이 성공적으로 생성되었습니다."
}
```

### 2.2 사용자 프로필 조회
```http
GET /users/profile/{user_id}
```

**Path Parameters**:
- `user_id` (string, required): 사용자 ID

**응답 예시**:
```json
{
  "user_id": "user_12345",
  "name": "김철수",
  "age": 75,
  "gender": "남성",
  "birth_place": "서울",
  "occupation": "교사",
  "family_info": "2남 1녀의 아버지",
  "created_at": "2025-08-03T11:35:17Z",
  "last_active": "2025-08-03T13:20:45Z",
  "total_sessions": 5,
  "autobiography_progress": 35.5
}
```

### 2.3 사용자 프로필 수정
```http
PUT /users/profile/{user_id}
Content-Type: application/json
```

**요청 본문**:
```json
{
  "occupation": "퇴직 교사",
  "family_info": "2남 1녀의 아버지, 손자 3명"
}
```

**응답 예시**:
```json
{
  "user_id": "user_12345",
  "updated": true,
  "updated_at": "2025-08-03T14:20:30Z",
  "updated_fields": ["occupation", "family_info"]
}
```

### 2.4 사용자 목록 조회
```http
GET /users/list
```

**Query Parameters**:
- `page` (integer, optional): 페이지 번호 (기본값: 1)
- `limit` (integer, optional): 페이지당 항목 수 (기본값: 20, 최대: 100)
- `search` (string, optional): 이름 검색어

**응답 예시**:
```json
{
  "total_users": 150,
  "current_page": 1,
  "total_pages": 8,
  "users": [
    {
      "user_id": "user_12345",
      "name": "김철수",
      "age": 75,
      "created_at": "2025-08-03T11:35:17Z",
      "last_active": "2025-08-03T13:20:45Z"
    }
  ]
}
```

---

## 💾 3. 세션 관리 API

### 3.1 대화 세션 생성
```http
POST /sessions/conversation
Content-Type: application/json
```

**요청 본문**:
```json
{
  "user_id": "user_12345",
  "conversation_type": "life_story",
  "session_settings": {
    "max_duration": 7200,
    "auto_save_interval": 300
  }
}
```

**파라미터 설명**:
- `user_id` (string, required): 사용자 ID
- `conversation_type` (string, optional): 대화 유형 ("life_story", "interview", "casual")
- `session_settings` (object, optional): 세션 설정
  - `max_duration` (integer): 최대 지속 시간 (초)
  - `auto_save_interval` (integer): 자동 저장 간격 (초)

**응답 예시**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "user_id": "user_12345",
  "conversation_type": "life_story",
  "created_at": "2025-08-03T11:35:17Z",
  "expires_at": "2025-08-03T13:35:17Z",
  "status": "active",
  "ai_server_notified": true
}
```

### 3.3 활성 세션 목록 조회
```http
GET /sessions/active
```

**Query Parameters**:
- `user_id` (string, optional): 특정 사용자의 세션만 조회
- `session_type` (string, optional): 세션 유형 필터 ("conversation", "autobiography")

**응답 예시**:
```json
{
  "total_active_sessions": 3,
  "sessions": [
    {
      "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
      "user_id": "user_12345",
      "type": "conversation",
      "created_at": "2025-08-03T11:35:17Z",
      "last_activity": "2025-08-03T12:45:30Z",
      "status": "active"
    },
    {
      "session_id": "auto_session_d564cec4-5901-4ec5-9dbf-c6f9712f775a",
      "user_id": "user_12345",
      "type": "autobiography",
      "created_at": "2025-08-03T10:20:15Z",
      "last_activity": "2025-08-03T12:50:22Z",
      "status": "active"
    }
  ]
}
```

### 3.4 세션 상세 정보 조회
```http
GET /sessions/{session_id}
```

**응답 예시**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "user_id": "user_12345",
  "type": "conversation",
  "status": "active",
  "created_at": "2025-08-03T11:35:17Z",
  "last_activity": "2025-08-03T12:45:30Z",
  "session_statistics": {
    "total_messages": 24,
    "duration": "1시간 10분",
    "topics_covered": ["childhood", "family", "career"]
  }
}
```

### 3.5 세션 종료
```http
DELETE /sessions/{session_id}
```

**응답 예시**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "status": "terminated",
  "terminated_at": "2025-08-03T13:45:17Z",
  "session_summary": {
    "duration": "2시간 10분",
    "total_messages": 24,
    "data_saved": true
  }
}
```

---

## 💬 4. 대화 데이터 관리 API

### 4.1 대화 내용 저장
```http
POST /conversations/save
Content-Type: application/json
```

**요청 본문**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "user_message": "어린 시절 6.25 전쟁 때 부산으로 피난을 갔었어요",
  "ai_response": "그 시절의 기억이 생생하게 전해집니다. 그때 기분은 어떠셨나요?",
  "timestamp": "2025-08-03T12:30:45Z",
  "metadata": {
    "chapter_classification": "society_country",
    "memory_classification": {
      "memory_type": "personal_experience",
      "importance_score": 0.8
    }
  }
}
```

**파라미터 설명**:
- `session_id` (string, required): 세션 ID
- `user_message` (string, required): 사용자 메시지
- `ai_response` (string, required): AI 응답
- `timestamp` (string, required): 타임스탬프 (ISO 8601)
- `metadata` (object, optional): 메타데이터
  - `chapter_classification` (string): 챕터 분류 결과
  - `memory_classification` (object): 기억 분류 정보

**응답 예시**:
```json
{
  "conversation_id": "conv_abc123",
  "saved": true,
  "saved_at": "2025-08-03T12:30:46Z",
  "message_count": 15
}
```

### 4.2 대화 히스토리 조회
```http
GET /conversations/history/{session_id}
```

**Query Parameters**:
- `limit` (integer, optional): 조회할 메시지 수 (기본값: 50, 최대: 200)
- `offset` (integer, optional): 시작 위치 (기본값: 0)
- `start_date` (string, optional): 시작 날짜 (ISO 8601)
- `end_date` (string, optional): 종료 날짜 (ISO 8601)

**응답 예시**:
```json
{
  "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
  "total_messages": 24,
  "conversations": [
    {
      "conversation_id": "conv_abc123",
      "user_message": "어린 시절 6.25 전쟁 때 부산으로 피난을 갔었어요",
      "ai_response": "그 시절의 기억이 생생하게 전해집니다. 그때 기분은 어떠셨나요?",
      "timestamp": "2025-08-03T12:30:45Z",
      "chapter_classification": "society_country"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "has_next": true
  }
}
```

### 4.3 대화 검색
```http
GET /conversations/search
```

**Query Parameters**:
- `user_id` (string, optional): 사용자 ID
- `keyword` (string, required): 검색 키워드
- `chapter` (string, optional): 챕터 필터
- `date_from` (string, optional): 시작 날짜
- `date_to` (string, optional): 종료 날짜

**응답 예시**:
```json
{
  "total_results": 12,
  "conversations": [
    {
      "conversation_id": "conv_abc123",
      "session_id": "session_b327993c-063f-45cf-8085-23a7871eb275",
      "user_message": "어린 시절 6.25 전쟁 때 부산으로 피난을 갔었어요",
      "ai_response": "그 시절의 기억이 생생하게 전해집니다...",
      "timestamp": "2025-08-03T12:30:45Z",
      "relevance_score": 0.95
    }
  ]
}
```

---

## 📖 5. 자서전 생성 관리 API

### 5.1 자서전 생성 작업 시작
```http
POST /autobiography/generate
Content-Type: application/json
```

**요청 본문**:
```json
{
  "session_id": "auto_session_d564cec4-5901-4ec5-9dbf-c6f9712f775a",
  "user_id": "user_12345",
  "generation_options": {
    "target_length": 50000,
    "include_photos": true,
    "narrative_style": "chronological",
    "emotional_depth": "high",
    "output_format": ["pdf", "docx"]
  }
}
```

**파라미터 설명**:
- `session_id` (string, required): 자서전 세션 ID
- `user_id` (string, required): 사용자 ID
- `generation_options` (object, optional): 생성 옵션
  - `target_length` (integer): 목표 글자 수 (10000-100000)
  - `include_photos` (boolean): 사진 포함 여부
  - `narrative_style` (string): 서술 스타일
  - `emotional_depth` (string): 감정 표현 깊이 ("low", "medium", "high")
  - `output_format` (array): 출력 형식 목록

**응답 예시**:
```json
{
  "task_id": "gen_task_abc123",
  "status": "queued",
  "created_at": "2025-08-03T12:35:17Z",
  "estimated_completion_time": "2025-08-03T13:05:17Z",
  "queue_position": 2,
  "message": "자서전 생성 작업이 대기열에 추가되었습니다."
}
```

### 5.2 자서전 생성 상태 확인
```http
GET /autobiography/status/{task_id}
```

**응답 예시**:
```json
{
  "task_id": "gen_task_abc123",
  "status": "in_progress",
  "progress": 65,
  "current_stage": "chapter_generation",
  "completed_chapters": 4,
  "total_chapters": 8,
  "estimated_remaining_time": "10 minutes",
  "started_at": "2025-08-03T12:40:17Z",
  "last_updated": "2025-08-03T12:55:30Z"
}
```

**상태 값**:
- `queued`: 대기 중
- `in_progress`: 진행 중
- `completed`: 완료
- `failed`: 실패
- `cancelled`: 취소됨

### 5.3 완성된 자서전 메타데이터 조회
```http
GET /autobiography/metadata/{task_id}
```

**응답 예시**:
```json
{
  "task_id": "gen_task_abc123",
  "user_id": "user_12345",
  "status": "completed",
  "completed_at": "2025-08-03T13:05:17Z",
  "autobiography_info": {
    "title": "김철수의 인생 이야기",
    "total_pages": 127,
    "word_count": 48500,
    "chapter_count": 8,
    "generation_time": "28 minutes"
  },
  "files": [
    {
      "format": "pdf",
      "file_size": "2.3MB",
      "download_url": "/autobiography/download/gen_task_abc123/pdf"
    },
    {
      "format": "docx",
      "file_size": "1.8MB",
      "download_url": "/autobiography/download/gen_task_abc123/docx"
    }
  ]
}
```

### 5.4 자서전 파일 다운로드
```http
GET /autobiography/download/{task_id}/{format}
```

**Path Parameters**:
- `task_id` (string, required): 작업 ID
- `format` (string, required): 파일 형식 ("pdf", "docx", "txt")

**응답**: 파일 다운로드 또는 다운로드 링크

---

## 📊 6. 통계 및 분석 API

### 6.1 사용자별 대화 통계
```http
GET /analytics/user/{user_id}/conversations
```

**Query Parameters**:
- `start_date` (string, optional): 시작 날짜 (ISO 8601)
- `end_date` (string, optional): 종료 날짜 (ISO 8601)
- `session_type` (string, optional): 세션 유형 필터

**응답 예시**:
```json
{
  "user_id": "user_12345",
  "period": {
    "start_date": "2025-08-01T00:00:00Z",
    "end_date": "2025-08-03T23:59:59Z"
  },
  "total_sessions": 5,
  "total_conversation_time": "4시간 35분",
  "total_messages": 120,
  "topics_covered": [
    {"topic": "childhood_memories", "frequency": 25},
    {"topic": "family_relationships", "frequency": 18},
    {"topic": "career_life", "frequency": 15}
  ],
  "memory_collection": {
    "total_memories": 45,
    "high_importance": 18,
    "medium_importance": 20,
    "low_importance": 7
  }
}
```

### 6.2 자서전 진행률 조회
```http
GET /analytics/autobiography/{session_id}/progress
```

**응답 예시**:
```json
{
  "session_id": "auto_session_d564cec4-5901-4ec5-9dbf-c6f9712f775a",
  "user_id": "user_12345",
  "overall_progress": 35.5,
  "life_stages_coverage": {
    "childhood": 80,
    "adolescence": 60,
    "young_adult": 40,
    "middle_age": 20,
    "elderly": 10
  },
  "chapter_status": [
    {
      "chapter_id": "ch_001",
      "chapter_name": "어린 시절",
      "progress": 90,
      "word_count": 2500,
      "memory_count": 8,
      "last_updated": "2025-08-03T12:45:30Z"
    },
    {
      "chapter_id": "ch_002",
      "chapter_name": "학창 시절",
      "progress": 70,
      "word_count": 1800,
      "memory_count": 6,
      "last_updated": "2025-08-03T11:20:15Z"
    }
  ],
  "estimated_completion": "2025-08-10T15:00:00Z"
}
```

### 6.3 시스템 전체 통계
```http
GET /analytics/system/overview
```

**Query Parameters**:
- `period` (string, optional): 조회 기간 ("daily", "weekly", "monthly")

**응답 예시**:
```json
{
  "period": "weekly",
  "date_range": {
    "start": "2025-07-28T00:00:00Z",
    "end": "2025-08-03T23:59:59Z"
  },
  "user_statistics": {
    "total_users": 150,
    "active_users": 45,
    "new_users": 8
  },
  "session_statistics": {
    "total_sessions": 320,
    "average_session_duration": "42분",
    "completion_rate": 78.5
  },
  "autobiography_statistics": {
    "total_generated": 12,
    "in_progress": 25,
    "average_generation_time": "32분"
  }
}
```

---

## 📁 7. 파일 관리 API

### 7.1 파일 업로드
```http
POST /files/upload
Content-Type: multipart/form-data
```

**요청 파라미터**:
- `file` (file, required): 업로드할 파일
- `user_id` (string, required): 사용자 ID
- `file_type` (string, required): 파일 유형 ("photo", "document", "audio")
- `description` (string, optional): 파일 설명

**응답 예시**:
```json
{
  "file_id": "file_xyz789",
  "original_filename": "family_photo.jpg",
  "stored_filename": "user_12345_1691234567_family_photo.jpg",
  "file_size": 2048576,
  "file_type": "photo",
  "upload_date": "2025-08-03T12:35:17Z",
  "download_url": "/files/download/file_xyz789"
}
```

### 7.2 파일 목록 조회
```http
GET /files/list/{user_id}
```

**Query Parameters**:
- `file_type` (string, optional): 파일 유형 필터
- `limit` (integer, optional): 조회할 파일 수 (기본값: 20)
- `offset` (integer, optional): 시작 위치

**응답 예시**:
```json
{
  "user_id": "user_12345",
  "total_files": 15,
  "files": [
    {
      "file_id": "file_xyz789",
      "original_filename": "family_photo.jpg",
      "file_type": "photo",
      "file_size": 2048576,
      "upload_date": "2025-08-03T12:35:17Z",
      "description": "가족 사진"
    }
  ]
}
```

### 7.3 파일 다운로드
```http
GET /files/download/{file_id}
```

**응답**: 파일 다운로드

### 7.4 파일 삭제
```http
DELETE /files/{file_id}
```

**응답 예시**:
```json
{
  "file_id": "file_xyz789",
  "deleted": true,
  "deleted_at": "2025-08-03T14:30:17Z"
}
```

---

## 🚨 8. 오류 처리

### 8.1 일반적인 HTTP 상태 코드

- **200 OK**: 요청 성공
- **201 Created**: 리소스 생성 성공
- **400 Bad Request**: 잘못된 요청 형식
- **401 Unauthorized**: 인증 필요
- **403 Forbidden**: 접근 권한 없음
- **404 Not Found**: 리소스를 찾을 수 없음
- **409 Conflict**: 리소스 충돌 (중복 생성 등)
- **422 Unprocessable Entity**: 유효성 검사 실패
- **500 Internal Server Error**: 서버 내부 오류
- **503 Service Unavailable**: 서비스 일시 불가

### 8.2 백엔드 특화 오류 코드

- `USER_NOT_FOUND`: 사용자를 찾을 수 없음
- `SESSION_EXPIRED`: 세션이 만료됨
- `SESSION_NOT_FOUND`: 세션을 찾을 수 없음
- `DATABASE_CONNECTION_ERROR`: 데이터베이스 연결 오류
- `FILE_UPLOAD_FAILED`: 파일 업로드 실패
- `AUTOBIOGRAPHY_GENERATION_FAILED`: 자서전 생성 실패
- `AI_SERVER_UNAVAILABLE`: AI 서버 연결 불가
- `STORAGE_QUOTA_EXCEEDED`: 저장 공간 한도 초과
- `INVALID_FILE_FORMAT`: 지원하지 않는 파일 형식
- `DUPLICATE_USER`: 중복된 사용자

### 8.3 오류 응답 형식
```json
{
  "detail": "사용자를 찾을 수 없습니다",
  "error_code": "USER_NOT_FOUND",
  "timestamp": "2025-08-03T11:35:17Z",
  "request_id": "req_abc123",
  "path": "/users/profile/user_99999"
}
```

---

## 🔐 9. 인증 및 보안

### 9.1 API 키 인증
```http
Authorization: Bearer your_api_key_here
```

### 9.2 사용자 세션 토큰
```http
X-Session-Token: session_token_here
```

### 9.3 관리자 인증
```http
X-Admin-Token: admin_token_here
```

### 9.4 데이터 보안
- 개인정보 암호화 저장 (AES-256)
- 파일 업로드 바이러스 스캔
- 정기적 데이터베이스 백업
- GDPR 준수 데이터 처리
- 사용자 데이터 삭제 요청 지원
- SQL 인젝션 방지
- XSS 공격 방지

---

## 📝 10. 사용 예시

### 10.1 사용자 등록 및 세션 생성 플로우
```bash
# 1. 사용자 프로필 생성
curl -X POST "http://localhost:8000/users/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "age": 75,
    "gender": "남성",
    "birth_place": "서울",
    "occupation": "교사"
  }'

# 응답: {"user_id": "user_12345", "profile_created": true}

# 2. 대화 세션 생성
curl -X POST "http://localhost:8000/sessions/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "conversation_type": "life_story"
  }'

# 응답: {"session_id": "session_abc123", "status": "active"}
```

### 10.2 자서전 생성 플로우
```bash
# 1. 자서전 세션 생성
curl -X POST "http://localhost:8000/sessions/autobiography" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "autobiography_settings": {
      "target_length": 50000,
      "narrative_style": "chronological"
    }
  }'

# 2. 자서전 생성 시작
curl -X POST "http://localhost:8000/autobiography/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "auto_session_xyz789",
    "user_id": "user_12345"
  }'

# 3. 생성 상태 확인
curl -X GET "http://localhost:8000/autobiography/status/gen_task_abc123"

# 4. 완성된 자서전 다운로드
curl -X GET "http://localhost:8000/autobiography/download/gen_task_abc123/pdf" \
  -o "autobiography.pdf"
```

### 10.3 통계 조회 플로우
```bash
# 사용자별 대화 통계
curl -X GET "http://localhost:8000/analytics/user/user_12345/conversations?start_date=2025-08-01T00:00:00Z"

# 자서전 진행률 조회
curl -X GET "http://localhost:8000/analytics/autobiography/auto_session_xyz789/progress"

# 시스템 전체 통계
curl -X GET "http://localhost:8000/analytics/system/overview?period=weekly"
```

---

## 🎯 11. 성능 및 제한사항

### 11.1 응답 시간 목표
- 기본 CRUD API: < 200ms
- 파일 업로드: < 5초 (50MB 기준)
- 데이터베이스 쿼리: < 500ms
- 자서전 생성 대기열 처리: < 1초
- 통계 API: < 2초

### 11.2 사용 제한
- 동시 사용자: 최대 1000명
- 파일 저장: 사용자당 최대 1GB
- 자서전 생성 대기열: 최대 50개 작업
- API 호출: 분당 최대 120회
- 세션 지속 시간: 최대 8시간

### 11.3 데이터베이스 사양
- PostgreSQL 13+
- 연결 풀: 최대 100개 연결
- 백업 주기: 일 1회, 주 1회 전체 백업
- 데이터 보존 기간: 5년
- 인덱스 최적화: 자동 VACUUM 설정

### 11.4 파일 저장소
- 지원 형식: JPG, PNG, PDF, DOCX, TXT
- 최대 파일 크기: 50MB
- 저장소 유형: AWS S3 또는 로컬 스토리지
- CDN 연동: CloudFront 지원

이 백엔드 API 문서를 통해 Life Bookshelf AI v2의 데이터 관리 및 비즈니스 로직을 효과적으로 구현할 수 있습니다.
