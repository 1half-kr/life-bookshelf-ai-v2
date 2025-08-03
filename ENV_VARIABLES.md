# 환경 변수 분석 및 가이드

## 📊 **환경 변수 필요성 분석**

### 🔴 **필수 변수 (시스템 작동에 반드시 필요)**

| 변수명 | 필요성 | 설명 | 기본값 |
|--------|--------|------|--------|
| `AWS_ACCESS_KEY_ID` | **필수** | AWS Bedrock 인증용 | 없음 |
| `AWS_SECRET_ACCESS_KEY` | **필수** | AWS Bedrock 인증용 | 없음 |

### 🟡 **권장 변수 (기본값 있지만 설정 권장)**

| 변수명 | 필요성 | 설명 | 기본값 |
|--------|--------|------|--------|
| `AWS_REGION` | 권장 | AWS 리전 설정 | `ap-northeast-2` |
| `DEBUG` | 권장 | 개발 모드 설정 | `false` |
| `LOG_LEVEL` | 권장 | 로그 상세도 | `INFO` |

### 🟢 **선택 변수 (기본값으로 충분)**

| 변수명 | 필요성 | 설명 | 기본값 |
|--------|--------|------|--------|
| `APP_NAME` | 선택 | 앱 이름 | `Life Bookshelf AI v2` |
| `APP_VERSION` | 선택 | 앱 버전 | `2.1.0` |
| `HOST` | 선택 | 서버 호스트 | `0.0.0.0` |
| `PORT` | 선택 | 서버 포트 | `3000` |
| `BEDROCK_MODEL_ID` | 선택 | 메인 LLM 모델 | `claude-3-sonnet-20240229` |
| `BEDROCK_FALLBACK_MODEL_ID` | 선택 | 백업 LLM 모델 | `claude-3-haiku-20240307` |
| `REDIS_URL` | 선택 | Redis 연결 URL | `redis://localhost:6379` |
| `REDIS_PASSWORD` | 선택 | Redis 비밀번호 | 없음 |
| `SESSION_TIMEOUT_HOURS` | 선택 | 세션 만료 시간 | `2` |
| `MAX_MESSAGE_LENGTH` | 선택 | 메시지 최대 길이 | `2000` |
| `LOG_FILE` | 선택 | 로그 파일 경로 | `logs/life-bookshelf-ai.log` |
| `CORS_ORIGINS` | 선택 | CORS 허용 Origin | `http://localhost:8000,http://127.0.0.1:8000` |
| `MAX_CONTEXT_MESSAGES` | 선택 | 컨텍스트 메시지 수 | `10` |
| `LLM_MAX_TOKENS` | 선택 | LLM 최대 토큰 | `1000` |
| `LLM_TEMPERATURE` | 선택 | LLM 창의성 | `0.7` |
| `LLM_TIMEOUT_SECONDS` | 선택 | LLM 타임아웃 | `30` |
| `INCLUDE_ANALYSIS` | 선택 | 분석 기능 활성화 | `true` |
| `INCLUDE_SUGGESTIONS` | 선택 | 제안 기능 활성화 | `true` |

### ❌ **사용하지 않는 변수 (제거 권장)**

| 변수명 | 상태 | 이유 |
|--------|------|------|
| `OPENAI_API_KEY` | 미사용 | AWS Bedrock 사용으로 대체 |
| `AZURE_OPENAI_API_KEY` | 미사용 | Azure OpenAI 미사용 |
| `LIFE_BOOKSHELF_AI_JWT_SECRET_KEY` | 미사용 | JWT 인증 미구현 |
| `VOICE_S3_BUCKET` | 미사용 | 음성 처리 기능 미구현 |
| `DATABASE_URL` | 미사용 | 현재 메모리 기반 세션 사용 |

## 🚀 **빠른 설정 가이드**

### **최소 설정 (필수만)**
```bash
# .env.development 파일에 추가
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
DEBUG=true
```

### **권장 설정**
```bash
# 위 필수 설정 + 아래 추가
AWS_REGION=ap-northeast-2
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000
```

### **프로덕션 설정**
```bash
# 권장 설정 + 아래 추가
DEBUG=false
LOG_LEVEL=INFO
SESSION_TIMEOUT_HOURS=1
LLM_TIMEOUT_SECONDS=20
```

## 🔒 **보안 주의사항**

1. **절대 커밋하지 말 것**: `.env.development`, `.env.production`
2. **실제 키 사용**: `your_actual_key` 같은 플레이스홀더 대신 실제 값
3. **권한 최소화**: AWS IAM에서 Bedrock 권한만 부여
4. **정기 교체**: API 키 정기적 교체 권장
