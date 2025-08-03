# Life Bookshelf AI v2

65세 이상 노년층을 위한 자서전 생성 시스템

## 🏗️ 시스템 구조

```
🗄️ 백엔드 서버 (Port 8000)    🤖 AI 서버 (Port 3000)
├── 사용자 관리                ├── 실시간 대화 처리
├── 세션 관리                  ├── 27개 챕터 분류
├── 대화 데이터 저장           └── 백엔드 연동
└── 자서전 생성 작업
```

## 📁 프로젝트 구조

```
life-bookshelf-ai-v2/
├── README.md                           # 프로젝트 가이드 (이 파일)
├── API_DOCUMENTATION.md                # 통합 API 가이드
├── BACKEND_API_DOCUMENTATION.md        # 백엔드 서버 API 문서
├── AI_SERVER_API_DOCUMENTATION.md      # AI 서버 API 문서
├── LICENSE                             # MIT 라이선스
├── .gitignore                          # Git 무시 파일 목록
└── serve/                              # 핵심 서버 코드
    ├── main.py                         # FastAPI 메인 서버
    ├── requirements.txt                # Python 의존성 목록
    ├── constants.py                    # 시스템 상수 정의
    ├── __init__.py                     # 패키지 초기화
    ├── .env.example                    # 환경 변수 템플릿
    ├── .env.development                # 개발 환경 설정
    ├── .env.production                 # 운영 환경 설정
    ├── .gitignore                      # 서버 전용 Git 무시 목록
    ├── llm/                            # LLM 연동 모듈
    │   └── bedrock_client.py           # AWS Bedrock 클라이언트
    ├── logs/                           # 로깅 시스템
    │   └── __init__.py                 # 로거 설정 및 초기화
    ├── conversation/                   # 대화 처리 모듈
    │   ├── elderly_chat.py             # 노년층 특화 대화 처리
    │   ├── context_manager.py          # 대화 컨텍스트 관리
    │   ├── conversation_router_v2.py   # 대화 API 라우터
    │   └── session_manager.py          # 세션 관리
    └── autobiography/                  # 자서전 생성 모듈
        ├── __init__.py                 # 패키지 초기화
        ├── autobiography_router.py     # 자서전 API 라우터
        └── improved_chapter_classifier.py  # 27개 챕터 분류기
```

## 📋 파일별 역할 설명

### 🔧 핵심 서버 파일

#### `serve/main.py`
- **역할**: FastAPI 메인 애플리케이션 서버
- **기능**: 
  - CORS 설정 및 미들웨어 구성
  - 라우터 등록 (conversation, autobiography)
  - 헬스체크 엔드포인트 제공
- **특이점**: 환경 변수를 가장 먼저 로드하여 설정 충돌 방지

#### `serve/requirements.txt`
- **역할**: Python 패키지 의존성 정의
- **주요 패키지**:
  - `fastapi`: 웹 프레임워크
  - `uvicorn`: ASGI 서버
  - `boto3`: AWS SDK
  - `redis`: 세션 저장소
  - `python-dotenv`: 환경 변수 관리

#### `serve/constants.py`
- **역할**: 시스템 전역 상수 정의
- **내용**: API 버전, 타임아웃 설정, 기본값 등

### 🤖 LLM 연동 모듈

#### `serve/llm/bedrock_client.py`
- **역할**: AWS Bedrock (Claude 3) 클라이언트
- **기능**:
  - Claude 3 Sonnet/Haiku 모델 연동
  - 토큰 사용량 모니터링
  - 오류 처리 및 재시도 로직
- **특이점**: 
  - 노년층 특화 프롬프트 템플릿 내장
  - 자동 폴백 메커니즘 (Sonnet → Haiku)

### 💬 대화 처리 모듈

#### `serve/conversation/elderly_chat.py`
- **역할**: 노년층 특화 대화 처리 엔진
- **기능**:
  - 노년층 친화적 응답 생성
  - 감정적 공감 표현
  - 후속 질문 자동 생성
- **특이점**: 
  - 말하기 속도와 어조 조절
  - 존댓말 일관성 유지
  - 기억 회상 유도 질문 패턴

#### `serve/conversation/context_manager.py`
- **역할**: 대화 컨텍스트 관리
- **기능**:
  - 대화 히스토리 추적
  - 주제 연속성 유지
  - 사용자 프로필 기반 맞춤화
- **특이점**: Redis 기반 분산 세션 관리

#### `serve/conversation/session_manager.py`
- **역할**: 세션 생명주기 관리
- **기능**:
  - 세션 생성/종료/연장
  - 타임아웃 처리
  - 세션 상태 동기화
- **특이점**: 
  - 자동 세션 정리 (2시간 후)
  - 백엔드 서버와 실시간 동기화

#### `serve/conversation/conversation_router_v2.py`
- **역할**: 대화 관련 API 엔드포인트
- **주요 API**:
  - `POST /conversation/chat`: 실시간 대화 처리
  - `PUT /conversation/context/{session_id}`: 컨텍스트 업데이트
  - `GET /conversation/health`: 서비스 상태 확인

### 📖 자서전 생성 모듈

#### `serve/autobiography/autobiography_router.py`
- **역할**: 자서전 관련 API 엔드포인트
- **주요 API**:
  - `POST /autobiography/text-input`: 텍스트 입력 처리
  - `GET /autobiography/health`: 서비스 상태 확인
- **특이점**: 백엔드 서버와의 비동기 통신 처리

#### `serve/autobiography/improved_chapter_classifier.py`
- **역할**: 27개 챕터 자동 분류 시스템
- **기능**:
  - 9개 대분류 × 3개 중분류 = 27개 챕터 분류
  - 키워드 기반 + AI 기반 하이브리드 분류
  - 신뢰도 점수 제공
- **특이점**: 
  - 노년층 언어 패턴 특화 학습
  - 실시간 분류 (< 1초)
  - 대안 챕터 제안 기능

### 📊 로깅 시스템

#### `serve/logs/__init__.py`
- **역할**: 통합 로깅 시스템 설정
- **기능**:
  - 레벨별 로그 분리 (DEBUG, INFO, ERROR)
  - 파일 로테이션 (일별/크기별)
  - 구조화된 로그 포맷 (JSON)
- **특이점**: 
  - 개인정보 자동 마스킹
  - 성능 메트릭 자동 수집

### ⚙️ 환경 설정 파일

#### `.env.example`
- **역할**: 환경 변수 템플릿
- **내용**: AWS 키, 데이터베이스 URL, Redis 설정 등

#### `.env.development` / `.env.production`
- **역할**: 환경별 설정 분리
- **차이점**:
  - 개발: 로컬 DB, 디버그 모드 활성화
  - 운영: 클라우드 DB, 최적화 설정

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
cd serve
pip install -r requirements.txt
cp .env.example .env.development
```

### 2. 환경 변수 설정
```bash
# .env.development 파일 편집
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-northeast-2
REDIS_URL=redis://localhost:6379
```

### 3. 서버 실행
```bash
# 개발 모드 (자동 재시작)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### 4. 서버 확인
```bash
# 헬스체크
curl http://localhost:3000/health

# API 문서 확인
open http://localhost:3000/docs
```

## 🧪 테스트 방법

### 1. 기본 헬스체크
```bash
# AI 서버 상태 확인
curl -X GET "http://localhost:3000/health"

# 대화 서비스 상태 확인
curl -X GET "http://localhost:3000/conversation/health"

# 자서전 서비스 상태 확인
curl -X GET "http://localhost:3000/autobiography/health"
```

### 2. 대화 처리 테스트
```bash
# 실시간 대화 테스트
curl -X POST "http://localhost:3000/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "message": "어린 시절 고향 이야기를 들려드리고 싶어요",
    "user_context": {
      "name": "김철수",
      "age": 75,
      "gender": "남성"
    }
  }'
```

### 3. 챕터 분류 테스트
```bash
# 챕터 분류 테스트
curl -X POST "http://localhost:3000/analysis/chapter-classification" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "대학교 1학년 때 처음 만난 친구들과의 추억",
    "user_context": {
      "age": 73,
      "gender": "남성"
    }
  }'
```

### 4. 성능 모니터링 테스트
```bash
# AI 성능 확인
curl -X GET "http://localhost:3000/monitoring/ai-performance"
```

### 5. 통합 테스트 스크립트
```bash
#!/bin/bash
# test_integration.sh

echo "=== Life Bookshelf AI v2 통합 테스트 ==="

# 1. 헬스체크
echo "1. 헬스체크..."
curl -s http://localhost:3000/health | jq '.status'

# 2. 대화 테스트
echo "2. 대화 처리 테스트..."
RESPONSE=$(curl -s -X POST "http://localhost:3000/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "message": "안녕하세요",
    "user_context": {"name": "테스트", "age": 75}
  }')
echo $RESPONSE | jq '.ai_response'

# 3. 챕터 분류 테스트
echo "3. 챕터 분류 테스트..."
CHAPTER=$(curl -s -X POST "http://localhost:3000/analysis/chapter-classification" \
  -H "Content-Type: application/json" \
  -d '{"text": "어린 시절 추억"}')
echo $CHAPTER | jq '.primary_classification.chapter_code'

echo "=== 테스트 완료 ==="
```

## ⚠️ 특이점 및 주의사항

### 🔒 보안 관련
1. **환경 변수 관리**
   - `.env` 파일은 절대 Git에 커밋하지 않음
   - AWS 키는 IAM 역할 사용 권장
   - Redis 연결에 비밀번호 설정 필수

2. **API 보안**
   - 프로덕션에서는 API 키 인증 필수
   - CORS 설정을 운영 도메인으로 제한
   - 요청 크기 제한 (2000자)

### 🚀 성능 관련
1. **메모리 관리**
   - Claude 3 모델 응답 캐싱 (Redis)
   - 세션 데이터 자동 정리 (2시간)
   - 로그 파일 자동 로테이션

2. **응답 시간**
   - 대화 처리: 평균 2-3초
   - 챕터 분류: 평균 1초 이하
   - 타임아웃 설정: 30초

### 🔧 운영 관련
1. **로그 모니터링**
   ```bash
   # 실시간 로그 확인
   tail -f serve/logs/life-bookshelf-ai.log
   
   # 에러 로그만 확인
   grep "ERROR" serve/logs/life-bookshelf-ai.log
   ```

2. **자동 재시작**
   - 개발: `--reload` 옵션 사용
   - 운영: systemd 또는 Docker 사용

3. **백업 전략**
   - Redis 데이터: 일 1회 백업
   - 로그 파일: 주 1회 아카이브
   - 환경 설정: Git으로 버전 관리

### 🐛 트러블슈팅

#### 자주 발생하는 문제들

1. **AWS Bedrock 연결 실패**
   ```bash
   # 해결 방법
   aws configure list  # AWS 설정 확인
   aws bedrock list-foundation-models --region ap-northeast-2  # 모델 접근 확인
   ```

2. **Redis 연결 실패**
   ```bash
   # 해결 방법
   redis-cli ping  # Redis 서버 확인
   # 응답: PONG이면 정상
   ```

3. **포트 충돌**
   ```bash
   # 포트 사용 확인
   lsof -i :3000
   
   # 프로세스 종료
   kill -9 <PID>
   ```

4. **메모리 부족**
   ```bash
   # 메모리 사용량 확인
   ps aux | grep python
   
   # 시스템 메모리 확인
   free -h
   ```

## 📚 API 문서

- **[통합 가이드](./API_DOCUMENTATION.md)**: 전체 시스템 아키텍처 및 사용법
- **[백엔드 API](./BACKEND_API_DOCUMENTATION.md)**: 데이터 관리 서버 API (Port 8000)
- **[AI 서버 API](./AI_SERVER_API_DOCUMENTATION.md)**: AI 처리 서버 API (Port 3000)

## 🎯 핵심 기능

1. **텍스트 기반 대화**: Claude 3 모델을 활용한 노년층 특화 대화
2. **27개 챕터 분류**: 체계적인 자서전 구성을 위한 자동 분류
3. **분리된 아키텍처**: 백엔드/AI 서버 독립 운영으로 확장성 확보
4. **실시간 처리**: 평균 3초 이내 응답으로 자연스러운 대화 경험
5. **컨텍스트 관리**: 대화 맥락 유지로 일관성 있는 상호작용

## 🔄 개발 워크플로우

1. **코드 수정** → `serve/` 폴더 내 파일 편집
2. **테스트** → 위의 테스트 방법 실행
3. **로그 확인** → `serve/logs/` 폴더 모니터링
4. **API 문서 업데이트** → 변경사항 반영
5. **배포** → Docker 또는 직접 배포

## 📞 지원

- **이슈 리포팅**: GitHub Issues 활용
- **API 문의**: API 문서의 예시 코드 참조
- **성능 문제**: 모니터링 API로 상태 확인 후 문의
