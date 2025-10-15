# Interview Chat V2 Flow

메트릭 기반 체계적 질문 생성 플로우

## 입력

```yaml
sessionId: string
question: object          # {id, material, type}
answer_text: string
metrics: object           # 세션 상태 (materials, chunks, global)
question_pool: array      # 질문 풀 (사용 안 함)
use_llm_keywords: boolean # LLM 키워드 추출 사용 여부 (기본: false)
```

## 출력

```yaml
next_question: object     # {id, material, type, text}
```

## 노드 구조

### 1. parse (01_parse_answer.py)
- 사용자 응답에서 키워드, 축(6W), 예시/구체성 플래그 추출
- 룰 기반 + LLM 기반 키워드 추출 지원
- 추출된 키워드는 소재별로 저장됨

### 2. update (02_update_metrics.py)
- 소재별 6W 축 완성도 갱신
- 예시(ex), 구체성(con) 플래그 업데이트
- 소재별 키워드 누적 저장 (최대 5개)
- 청크 가중치 증가

### 3. select (03_select_and_generate.py)
- **소재 선택 알고리즘**:
  - 1순위: 직전 소재 지속 (3번 미만 & 미완료)
  - 2순위: chunk_weight 내림차순
  - 3순위: 전체 중 진행도 낮은 소재
- **타입 선택**: how > ex > con > 기타
- **질문 생성**: standard/generate_interview_questions_v2 flow 호출
  - 소재별 저장된 키워드를 활용하여 LLM이 자연스러운 질문 생성
  - 키워드가 없으면 소재만으로 질문 생성
- 연속 질문 제한 (동일 소재 최대 3회)

## 테스트

```bash
# Visual Editor에서 flow.dag.yaml 열기
# Test Run 실행
```

## 주요 특징

- **키워드 기반 질문**: 사용자가 언급한 키워드를 소재별로 누적하여 구체적인 질문 생성
- **LLM 활용**: standard worker를 통해 자연스럽고 다양한 질문 생성
- **즉시 생성**: 질문을 미리 만들지 않고 필요할 때 1개만 생성
- **메트릭 추적**: 6W 축 완성도를 추적하여 체계적인 인터뷰 진행

## 메트릭 구조

```python
{
  "materials": {
    "소재명": {
      "category_name": "카테고리",
      "chunk_name": "청크",
      "w1": 0,  # when
      "w2": 0,  # how
      "w3": 0,  # who
      "w4": 0,  # what
      "w5": 0,  # where
      "w6": 0,  # why
      "ex": 0,  # 예시
      "con": 0, # 구체성
      "utter_freq": 0,
      "material_count": 0,  # 완료 여부
      "themes": [],
      "keywords": []  # 소재별 누적 키워드 (최대 5개)
    }
  },
  "chunks": {
    "카테고리::청크": {
      "category_name": "카테고리",
      "chunk_name": "청크",
      "chunk_weight": 0
    }
  },
  "global": {
    "last_material": "",
    "last_material_streak": 0,
    "theme_initialized": false
  },
  "theme": "테마명"
}
```

## 질문 생성 방식

1. **응답 분석**: 사용자 응답에서 키워드 추출 → 해당 소재에 저장
2. **소재/타입 선택**: 알고리즘에 따라 다음 질문할 소재와 타입 결정
3. **LLM 질문 생성**: `standard/generate_interview_questions_v2` flow 호출
   - 소재명, 타입, 저장된 키워드를 전달
   - LLM이 키워드를 자연스럽게 활용하여 질문 생성
   - 템플릿 패턴 사용 금지 ("~에 대해 방법/과정을..." 같은 표현 X)
4. **즉시 반환**: 생성된 질문 1개만 반환 (질문 풀 미사용)
