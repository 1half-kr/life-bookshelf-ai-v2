# 📚 Life Bookshelf AI v2 - API 완전 가이드 (분리된 아키텍처)

## 🎯 시스템 개요
65세 이상 노년층을 위한 텍스트 기반 AI 자서전 생성 시스템

## 🏗️ 분리된 서버 아키텍처

### 🗄️ 백엔드 서버 (데이터 관리)
**기본 URL**: `http://localhost:8000`  
**API 문서**: `http://localhost:8000/docs` (Swagger UI)  
**상세 문서**: [BACKEND_API_DOCUMENTATION.md](./BACKEND_API_DOCUMENTATION.md)

**담당 기능**:
- 사용자 데이터 관리 (CRUD)
- 세션 생성 및 관리
- 대화 데이터 저장 및 조회
- 자서전 생성 작업 관리
- 파일 저장소 관리
- 통계 및 분석 데이터 제공

### 🤖 AI 서버 (실시간 처리)
**기본 URL**: `http://localhost:3000`  
**API 문서**: `http://localhost:3000/docs` (Swagger UI)  
**상세 문서**: [AI_SERVER_API_DOCUMENTATION.md](./AI_SERVER_API_DOCUMENTATION.md)

**담당 기능**:
- 실시간 대화 처리 (Claude 3)
- 27개 챕터 자동 분류
- 백엔드 서버 연동
- AI 성능 모니터링
- 컨텍스트 관리

---

## 📋 서버별 API 매핑

### 🗄️ 백엔드 서버 API (Port 8000)

| 카테고리 | API 엔드포인트 | 설명 |
|---------|---------------|------|
| **시스템 상태** | `GET /health` | 백엔드 서버 상태 확인 |
| **사용자 관리** | `POST /users/profile` | 사용자 프로필 생성 |
| | `GET /users/profile/{user_id}` | 사용자 프로필 조회 |
| | `PUT /users/profile/{user_id}` | 사용자 프로필 수정 |
| | `GET /users/list` | 사용자 목록 조회 |
| **세션 관리** | `POST /sessions/conversation` | 대화 세션 생성 |
| | `POST /sessions/autobiography` | 자서전 세션 생성 |
| | `GET /sessions/active` | 활성 세션 목록 조회 |
| | `GET /sessions/{session_id}` | 세션 상세 정보 조회 |
| | `DELETE /sessions/{session_id}` | 세션 종료 |
| **대화 데이터** | `POST /conversations/save` | 대화 내용 저장 |
| | `GET /conversations/history/{session_id}` | 대화 히스토리 조회 |
| | `GET /conversations/search` | 대화 검색 |
| **자서전 생성** | `POST /autobiography/generate` | 자서전 생성 작업 시작 |
| | `GET /autobiography/status/{task_id}` | 자서전 생성 상태 확인 |
| | `GET /autobiography/metadata/{task_id}` | 자서전 메타데이터 조회 |
| | `GET /autobiography/download/{task_id}/{format}` | 완성된 자서전 다운로드 |
| | `DELETE /autobiography/cancel/{task_id}` | 자서전 생성 작업 취소 |
| **통계 분석** | `GET /analytics/user/{user_id}/conversations` | 사용자별 대화 통계 |
| | `GET /analytics/autobiography/{session_id}/progress` | 자서전 진행률 조회 |
| | `GET /analytics/system/overview` | 시스템 전체 통계 |
| **파일 관리** | `POST /files/upload` | 파일 업로드 |
| | `GET /files/list/{user_id}` | 파일 목록 조회 |
| | `GET /files/download/{file_id}` | 파일 다운로드 |
| | `DELETE /files/{file_id}` | 파일 삭제 |

### 🤖 AI 서버 API (Port 3000)

| 카테고리 | API 엔드포인트 | 설명 |
|---------|---------------|------|
| **시스템 상태** | `GET /health` | AI 서버 상태 확인 |
| | `GET /conversation/health` | 대화 서비스 상태 확인 |
| **실시간 대화** | `POST /conversation/chat` | 실시간 대화 처리 |
| | `PUT /conversation/context/{session_id}` | 대화 컨텍스트 업데이트 |
| **AI 분석** | `POST /analysis/chapter-classification` | 27개 챕터 분류 |
| **백엔드 연동** | `POST /backend/save-conversation` | 대화 데이터 백엔드 전송 |
| | `POST /backend/sync-session` | 세션 상태 동기화 |
| **성능 모니터링** | `GET /monitoring/ai-performance` | AI 처리 성능 조회 |

---

## 🔄 통합 사용 플로우

### 1. 사용자 등록 및 세션 시작
```mermaid
sequenceDiagram
    participant Client as 📱 클라이언트
    participant Backend as 🗄️ 백엔드 (8000)
    participant AI as 🤖 AI 서버 (3000)

    Client->>Backend: POST /users/profile (사용자 생성)
    Backend->>Client: user_id 반환
    
    Client->>Backend: POST /sessions/conversation (세션 생성)
    Backend->>Client: session_id 반환
    Backend->>AI: 세션 정보 동기화
```

### 2. 텍스트 기반 대화 플로우
```mermaid
sequenceDiagram
    participant Client as 📱 클라이언트
    participant Backend as 🗄️ 백엔드 (8000)
    participant AI as 🤖 AI 서버 (3000)

    Client->>AI: POST /conversation/chat (대화 처리)
    AI->>Backend: POST /backend/save-conversation (대화 저장)
    AI->>Client: AI 응답 + 챕터 분류 결과 반환
```

### 3. 자서전 생성 플로우
```mermaid
sequenceDiagram
    participant Client as 📱 클라이언트
    participant Backend as 🗄️ 백엔드 (8000)
    participant AI as 🤖 AI 서버 (3000)

    Client->>Backend: POST /sessions/autobiography (자서전 세션 생성)
    Backend->>Client: session_id 반환
    
    Note over Client,AI: 여러 차례 대화 진행
    
    Client->>Backend: POST /autobiography/generate (자서전 생성 시작)
    Backend->>Client: task_id 반환
    
    Client->>Backend: GET /autobiography/status/{task_id} (상태 확인)
    Backend->>Client: 진행률 반환
    
    Client->>Backend: GET /autobiography/download/{task_id} (완성본 다운로드)
    Backend->>Client: 파일 다운로드
```

---

## 💡 개발자 가이드

### 클라이언트 개발 시 고려사항

1. **서버 분리 인식**: 백엔드(8000)와 AI 서버(3000)를 구분하여 호출
2. **세션 관리**: 백엔드에서 세션을 생성하고, AI 서버에서 실시간 처리
3. **오류 처리**: 각 서버별로 다른 오류 코드와 처리 방식
4. **성능 최적화**: AI 서버는 실시간 처리, 백엔드는 데이터 관리에 특화
5. **타임아웃 설정**: AI 서버는 더 긴 타임아웃 필요 (AI 처리 시간 고려)

### 권장 클라이언트 구조
```javascript
// 클라이언트 설정 예시
const config = {
  backendServer: 'http://localhost:8000',
  aiServer: 'http://localhost:3000',
  timeout: {
    backend: 10000,  // 10초
    ai: 30000        // 30초 (AI 처리 시간 고려)
  }
};

// API 호출 함수 예시
class LifeBookshelfAPI {
  // 백엔드 API 호출
  async createUser(userData) {
    return await fetch(`${config.backendServer}/users/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
      timeout: config.timeout.backend
    });
  }

  async createSession(userId, sessionType = 'conversation') {
    return await fetch(`${config.backendServer}/sessions/${sessionType}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
      timeout: config.timeout.backend
    });
  }

  // AI 서버 API 호출
  async processConversation(sessionId, message, userContext) {
    return await fetch(`${config.aiServer}/conversation/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: sessionId, 
        message,
        user_context: userContext
      }),
      timeout: config.timeout.ai
    });
  }

  async classifyChapter(text, userContext) {
    return await fetch(`${config.aiServer}/analysis/chapter-classification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, user_context: userContext }),
      timeout: config.timeout.ai
    });
  }
}
```

### 오류 처리 전략
```javascript
class APIErrorHandler {
  static handleBackendError(error) {
    switch(error.error_code) {
      case 'USER_NOT_FOUND':
        return '사용자를 찾을 수 없습니다.';
      case 'SESSION_EXPIRED':
        return '세션이 만료되었습니다. 다시 로그인해주세요.';
      case 'DATABASE_CONNECTION_ERROR':
        return '일시적인 서버 오류입니다. 잠시 후 다시 시도해주세요.';
      default:
        return '알 수 없는 오류가 발생했습니다.';
    }
  }

  static handleAIError(error) {
    switch(error.error_code) {
      case 'AI_MODEL_UNAVAILABLE':
        return 'AI 서비스가 일시적으로 사용할 수 없습니다.';
      case 'CHAPTER_CLASSIFICATION_FAILED':
        return '챕터 분류에 실패했습니다. 다시 시도해주세요.';
      case 'MESSAGE_TOO_LONG':
        return '메시지가 너무 깁니다. 2000자 이내로 입력해주세요.';
      default:
        return 'AI 처리 중 오류가 발생했습니다.';
    }
  }
}
```

---

## 🔧 배포 및 운영

### Docker Compose 예시
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/life_bookshelf
      - AI_SERVER_URL=http://ai-server:3000
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  ai-server:
    build: ./ai-server
    ports:
      - "3000:3000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=ap-northeast-2
      - BACKEND_SERVER_URL=http://backend:8000
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=life_bookshelf
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - ai-server
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 로드 밸런싱 고려사항
- **백엔드 서버**: 수평 확장 가능 (Stateless)
- **AI 서버**: GPU 리소스 고려한 확장 (세션 상태는 Redis 공유)
- **데이터베이스**: 읽기 복제본 활용
- **Redis**: 클러스터 모드 고려

### Nginx 설정 예시
```nginx
upstream backend {
    server backend:8000;
}

upstream ai-server {
    server ai-server:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api/backend/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_timeout 30s;
    }

    location /api/ai/ {
        proxy_pass http://ai-server/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_timeout 60s;  # AI 처리 시간 고려
    }
}
```

---

## 📊 모니터링 및 로깅

### 주요 메트릭
- **백엔드 서버**: 응답 시간, 데이터베이스 연결, 파일 저장소 상태
- **AI 서버**: AI 모델 응답 시간, 챕터 분류 성능
- **통합 메트릭**: 전체 사용자 플로우 완료율, 오류율

### 로그 수집 예시
```bash
# 백엔드 서버 로그
tail -f /var/log/life-bookshelf/backend.log

# AI 서버 로그  
tail -f /var/log/life-bookshelf/ai-server.log

# 통합 로그 분석
grep "ERROR" /var/log/life-bookshelf/*.log | tail -20

# 성능 모니터링
curl -s http://localhost:8000/health | jq '.services'
curl -s http://localhost:3000/monitoring/ai-performance | jq '.current_performance'
```

### Prometheus 메트릭 예시
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'ai-server'
    static_configs:
      - targets: ['ai-server:3000']
    metrics_path: '/metrics'
```

---

## 🚀 마이그레이션 가이드

기존 통합 서버에서 분리된 아키텍처로 마이그레이션하는 경우:

### 1단계: 데이터 마이그레이션
```sql
-- 기존 데이터를 백엔드 서버 스키마로 마이그레이션
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    session_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    conversation_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES sessions(session_id),
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    chapter_classification VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2단계: API 호출 변경
```javascript
// 기존 (통합 서버)
const response = await fetch('http://localhost:3000/conversation/start', {
  method: 'POST',
  body: JSON.stringify(userData)
});

// 변경 후 (분리된 서버)
// 1. 백엔드에서 사용자 생성
const userResponse = await fetch('http://localhost:8000/users/profile', {
  method: 'POST',
  body: JSON.stringify(userData)
});

// 2. 백엔드에서 세션 생성
const sessionResponse = await fetch('http://localhost:8000/sessions/conversation', {
  method: 'POST',
  body: JSON.stringify({ user_id: userResponse.user_id })
});

// 3. AI 서버에서 대화 처리
const chatResponse = await fetch('http://localhost:3000/conversation/chat', {
  method: 'POST',
  body: JSON.stringify({ 
    session_id: sessionResponse.session_id,
    message: userMessage
  })
});
```

### 3단계: 환경 설정 업데이트
```bash
# .env 파일 업데이트
# 백엔드 서버
DATABASE_URL=postgresql://user:password@localhost:5432/life_bookshelf
AI_SERVER_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379

# AI 서버
BACKEND_SERVER_URL=http://localhost:8000
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-northeast-2
```

---

## 📈 성능 최적화 가이드

### 백엔드 서버 최적화
- 데이터베이스 인덱스 최적화
- 연결 풀 크기 조정
- 캐싱 전략 (Redis 활용)
- 파일 업로드 최적화

### AI 서버 최적화
- 모델 로딩 최적화
- 배치 처리 구현
- GPU 메모리 관리
- 응답 캐싱

### 네트워크 최적화
- CDN 활용
- 압축 설정
- Keep-Alive 연결
- 로드 밸런싱

이 통합 API 문서를 통해 Life Bookshelf AI v2의 분리된 아키텍처를 이해하고 효과적으로 활용할 수 있습니다.
