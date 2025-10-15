# Interview Chat V2 API 테스트 가이드

## 사전 준비

### 1. 서버 실행
```bash
cd serve
python -m uvicorn main:app --env-file .env.development --port 3000
```

### 2. JWT 토큰 생성
```bash
python generate_test_token.py
```

출력된 토큰을 복사하세요.

### 3. Swagger UI 접속
http://localhost:3000/docs

---

## 테스트 시나리오

### Step 1: 인증 설정

1. Swagger UI 우측 상단 **Authorize** 버튼 클릭
2. Value 입력란에 토큰 입력 (Bearer 제외하고 토큰만)
3. **Authorize** 클릭
4. **Close** 클릭

---

### Step 2: 첫 질문 생성

**엔드포인트**: `POST /api/v2/interviews/interview-chat`

**Request Body**:
```json
{
  "question": {
    "id": "q-start",
    "material": "좋아했던 과목",
    "type": "open"
  },
  "answer_text": "",
  "metrics": {
    "materials": {
      "좋아했던 과목": {
        "category_name": "학업",
        "chunk_name": "전공 공부",
        "w1": 0,
        "w2": 0,
        "w3": 0,
        "w4": 0,
        "w5": 0,
        "w6": 0,
        "ex": 0,
        "con": 0,
        "material_count": 0,
        "utter_freq": 0,
        "themes": ["나의 대학 시절"]
      }
    },
    "chunks": {
      "학업::전공 공부": {
        "category_name": "학업",
        "chunk_name": "전공 공부",
        "chunk_weight": 0
      }
    },
    "global": {
      "last_material": null,
      "last_material_streak": 0,
      "theme_initialized": false
    },
    "theme": "나의 대학 시절"
  },
  "question_pool": [],
  "use_llm_keywords": false
}
```

**예상 응답**:
```json
{
  "next_question": {
    "id": "q-onfly",
    "material": "좋아했던 과목",
    "type": "how",
    "text": "좋아했던 과목에 대해 방법/과정을 더 자세히 들려주실 수 있을까요?"
  },
  "pool_to_save": [],
  "metrics_to_save": {
    "materials": {...},
    "chunks": {...},
    "global": {...},
    "theme": "나의 대학 시절"
  }
}
```

**확인 사항**:
- ✅ 200 OK 응답
- ✅ next_question이 생성됨
- ✅ question.text가 자연스러운 질문
- ✅ metrics_to_save와 pool_to_save 반환

---

### Step 3: 대화 진행 (다음 질문 생성)

**엔드포인트**: `POST /api/v2/interviews/interview-chat`

**중요**: Step 2의 응답에서 받은 `next_question`을 이번 요청의 `question`에 넣고, `metrics`에는 이전 응답의 `metrics_to_save`를 넣어야 합니다!

**Request Body**:
```json
{
  "question": {
    "id": "q-onfly",
    "material": "좋아했던 과목",
    "type": "how"
  },
  "answer_text": "저는 데이터베이스 수업을 정말 좋아했어요. 김교수님이 가르치셨는데, 실습 위주로 진행되어서 재미있었습니다. 2학년 2학기 때 들었던 것 같아요.",
  "metrics": {
    "materials": {
      "좋아했던 과목": {
        "category_name": "학업",
        "chunk_name": "전공 공부",
        "w1": 0,
        "w2": 0,
        "w3": 0,
        "w4": 0,
        "w5": 0,
        "w6": 0,
        "ex": 0,
        "con": 0,
        "material_count": 0,
        "utter_freq": 0,
        "themes": ["나의 대학 시절"]
      }
    },
    "chunks": {
      "학업::전공 공부": {
        "category_name": "학업",
        "chunk_name": "전공 공부",
        "chunk_weight": 10
      }
    },
    "global": {
      "last_material": "좋아했던 과목",
      "last_material_streak": 1,
      "theme_initialized": true
    },
    "theme": "나의 대학 시절"
  },
  "question_pool": [],
  "use_llm_keywords": false
}
```

**예상 응답**:
```json
{
  "next_question": {
    "id": "q-onfly",
    "material": "좋아했던 과목",
    "type": "ex",
    "text": "좋아했던 과목에 대한 구체적인 사례를 한 가지 들려주실 수 있을까요?"
  },
  "pool_to_save": [],
  "metrics_to_save": {...}
}
```

**확인 사항**:
- ✅ 200 OK 응답
- ✅ next_question이 생성됨
- ✅ metrics_to_save와 pool_to_save 반환됨 (백엔드는 다음 요청 시 사용)

---

### Step 4: 추가 대화 반복

동일한 방식으로 Step 3을 반복하며, 매번 이전 응답의 `metrics_to_save`를 다음 요청의 `metrics`로 전달합니다.

**확인 사항**:
- ✅ 각 턴마다 metrics가 업데이트됨 (w1~w6, ex, con 값 변화)
- ✅ chunk_weight가 증가함
- ✅ 다양한 type의 질문이 생성됨 (how, ex, con, who, why, when, where, what)

---

## 트러블슈팅

### 401 Unauthorized
- JWT 토큰이 올바르게 설정되었는지 확인
- `generate_test_token.py`로 새 토큰 생성

### 500 Internal Server Error
- 서버 콘솔 로그 확인
- OpenAI API 키가 올바른지 확인
- flow.dag.yaml 파일 경로 확인

### Flow 실행 오류
- `flows/interviews/chat/interview_chat_v2/` 디렉토리 존재 확인
- requirements.txt 패키지 설치 확인

---

## 성공 기준

✅ Step 1: JWT 인증 성공  
✅ Step 2: 첫 질문 생성 성공  
✅ Step 3: 다음 질문 생성 성공  
✅ Step 4: 대화 반복 테스트 성공  

모든 단계가 200 OK를 반환하면 API가 정상 작동하는 것입니다!
