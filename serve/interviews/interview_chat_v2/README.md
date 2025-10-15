# Interview Chat V2 API

메트릭 기반 체계적 질문 생성 시스템

## 아키텍처 개요

```
[백엔드] --session/start-----> [AI 서버]
      (categories + metrics)    ↓
                           [메모리에 metrics 저장]
                                ↓
[백엔드] <--first_question----- [AI 서버]
    ↓
  [DB에 metrics 저장]

[백엔드] --interview-chat----> [AI 서버]
      (question, answer)        ↓
                           [메모리에서 metrics 로드]
                                ↓
                           [metrics 업데이트]
                                ↓
                           [pool 업데이트]
                                ↓
[백엔드] <--next_question------ [AI 서버]

[백엔드] --session/end-------> [AI 서버]
                                ↓
                           [메모리에서 metrics 조회]
                                ↓
[백엔드] <--final_metrics----- [AI 서버]
         <--pool_to_save-------
    ↓
  [DB에 최종 저장]
```

## 엔드포인트

### 1. 세션 시작
`POST /api/v2/interviews/session/start`

### 2. 대화 진행
`POST /api/v2/interviews/interview-chat`

### 3. 세션 종료
`POST /api/v2/interviews/session/end`

## 세션 시작 요청 예시

```json
{
  "sessionId": "sess-001",
  "theme": "finance",
  "categories": {
    "1": {
      "category_num": 1,
      "category_name": "부모",
      "chunks": {
        "1": {
          "chunk_num": 1,
          "chunk_name": "성격",
          "materials": {
            "1": {
              "material_num": 1,
              "material_name": "출생지",
              "w": [0, 0, 0, 0, 0, 0],
              "ex": 0,
              "con": 0,
              "material_count": 0,
              "utter_freq": 0
            }
          }
        }
      },
      "chunk_weight": {}
    }
  },
  "metrics": {
    "sessionId": "sess-001",
    "theme": "finance",
    "categories": { ... },
    "engine_state": {
      "last_material_id": [],
      "last_material_streak": 0,
      "epsilon": 0.1
    },
    "asked_total": 0,
    "policyVersion": "v1.2.0"
  }
}
```

## 세션 시작 응답 예시

```json
{
  "sessionId": "sess-001",
  "first_question": {
    "id": "q-48b8",
    "material": "출생지",
    "type": "when",
    "text": "출생지에 대해 시기/때를 더 자세히 들려주실 수 있을까요?"
  }
}
```

## 대화 진행 요청 예시

```json
{
  "sessionId": "sess-001",
  "question": {
    "id": "q-47ab",
    "material": "출생지",
    "type": "why"
  },
  "answerText": "초등학교 때 어머니가...",
  "question_pool": [],
  "use_llm_keywords": false
}
```

## 대화 진행 응답 예시

```json
{
  "next_question": {
    "id": "q-48b8",
    "material": "금융",
    "type": "when",
    "text": "첫 직장 시절 적금을 시작하게 된 계기는 언제였나요?"
  }
}
```

## 세션 종료 요청 예시

```json
{
  "sessionId": "sess-001"
}
```

## 세션 종료 응답 예시

```json
{
  "sessionId": "sess-001",
  "final_metrics": {
    "sessionId": "sess-001",
    "theme": "finance",
    "categories": {
      "1": {
        "category_num": 1,
        "category_name": "부모",
        "chunks": {
          "1": {
            "chunk_num": 1,
            "chunk_name": "성격",
            "materials": {
              "1": {
                "material_num": 1,
                "material_name": "출생지",
                "w": [1, 1, 1, 0, 1, 1],
                "ex": 1,
                "con": 1,
                "material_count": 5,
                "utter_freq": 20
              }
            }
          }
        },
        "chunk_weight": {"1": 15}
      }
    },
    "engine_state": {
      "last_material_id": [1],
      "last_material_streak": 3,
      "epsilon": 0.1
    },
    "asked_total": 10,
    "policyVersion": "v1.2.0"
  },
  "pool_to_save": [
    {
      "id": "q-xxx",
      "material": "출생지",
      "keywords": ["초등학교", null, null],
      "type": "why",
      "text": "...",
      "source": "llm",
      "status": "queued"
    }
  ]
}
```

## 백엔드 처리

### 세션 시작
1. 사용자 선택 카테고리와 초기 metrics를 AI 서버로 전달
2. `first_question`을 받아 사용자에게 전달
3. metrics는 백엔드 DB에 저장

### 대화 진행
1. 사용자 답변과 이전 질문 정보를 AI 서버로 전달
2. `next_question`을 사용자에게 전달
3. **metrics와 pool은 AI 서버가 내부적으로 관리**

### 세션 종료
1. AI 서버로 세션 종료 요청
2. `final_metrics`와 `pool_to_save`를 받아 DB에 저장

## 주요 변경사항 (v2)

- **Metrics 관리**: 백엔드가 session/start에서 초기 metrics 전달, session/end에서 최종 metrics 수신
- **AI 서버 내부 관리**: interview-chat 동안 metrics와 pool을 세션별로 메모리/캐시에 저장
- **간소화된 API**: interview-chat 요청/응답에서 metrics와 pool 제거
