# Interview Chat V1

대화 히스토리 기반 인터뷰 질문 생성 플로우

## 개요

사용자 정보, 챕터 정보, 대화 히스토리를 기반으로 LLM이 자유롭게 다음 질문을 생성합니다.

## 입력

```yaml
user_info: object           # 사용자 정보 (이름, 생년월일, 성별, 직업 등)
chapter_info: object        # 챕터 정보 (제목, 설명)
sub_chapter_info: object    # 서브챕터 정보 (제목, 설명)
conversation_history: list  # 대화 히스토리 [{content, conversation_type}]
current_answer: string      # 사용자의 현재 답변
```

## 출력

```yaml
next_question: string       # 다음 인터뷰 질문 (한국어)
```

## 특징

- LLM이 대화 맥락을 파악하여 자연스러운 질문 생성
- 사용자 배경 정보를 고려한 개인화된 질문
- 반복 질문 방지
- 따뜻하고 존중하는 어조

## 사용

```bash
# Visual Editor에서 flow.dag.yaml 열기
# Test Run 실행
```

## API 엔드포인트

`POST /api/v1/interviews/interview-chat`
