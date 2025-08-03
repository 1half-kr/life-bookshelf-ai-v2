# Pipeline-oriented Architecture for Life Bookshelf AI v2

## 🏗️ **아키텍처 개요**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│  Message Broker  │───▶│ Argo Workflows  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ FastAPI Service │    │   Redis/Kafka    │    │  K8s Cluster    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔄 **Pipeline 흐름**

### **1. Conversation Pipeline**
```yaml
User Input → Validation → Context Loading → LLM Processing → Response Generation → Storage
```

### **2. Analysis Pipeline**
```yaml
Message → Preprocessing → Chapter Classification → Emotion Analysis → Memory Scoring → Results
```

### **3. Autobiography Pipeline**
```yaml
Conversations → Content Extraction → Chapter Organization → Text Generation → PDF Creation
```

## 📁 **프로젝트 구조**

```
life-bookshelf-ai-v2/
├── serve/                          # 기존 FastAPI 서비스 (API Gateway 역할)
├── pipelines/                      # Pipeline 구현체들
│   ├── conversation/               # 대화 처리 파이프라인
│   │   ├── steps/                  # 개별 처리 단계들
│   │   │   ├── validation.py       # 입력 검증
│   │   │   ├── context_loader.py   # 컨텍스트 로딩
│   │   │   ├── llm_processor.py    # LLM 처리
│   │   │   └── response_builder.py # 응답 생성
│   │   ├── pipeline.py             # 파이프라인 오케스트레이션
│   │   └── config.yaml             # 파이프라인 설정
│   ├── analysis/                   # 분석 파이프라인
│   │   ├── steps/
│   │   │   ├── preprocessor.py     # 전처리
│   │   │   ├── chapter_classifier.py # 챕터 분류
│   │   │   ├── emotion_analyzer.py # 감정 분석
│   │   │   └── memory_scorer.py    # 기억 중요도 평가
│   │   └── pipeline.py
│   └── autobiography/              # 자서전 생성 파이프라인
│       ├── steps/
│       │   ├── content_extractor.py # 내용 추출
│       │   ├── chapter_organizer.py # 챕터 구성
│       │   ├── text_generator.py   # 텍스트 생성
│       │   └── pdf_creator.py      # PDF 생성
│       └── pipeline.py
├── workflows/                      # Argo Workflow 정의
│   ├── templates/                  # 워크플로우 템플릿
│   │   ├── conversation-workflow.yaml
│   │   ├── analysis-workflow.yaml
│   │   └── autobiography-workflow.yaml
│   └── manifests/                  # K8s 매니페스트
│       ├── workflow-controller.yaml
│       └── service-accounts.yaml
├── services/                       # 지원 서비스들
│   ├── api-gateway/                # API 게이트웨이
│   ├── message-broker/             # 메시지 브로커
│   └── storage/                    # 스토리지 서비스
└── shared/                         # 공통 모듈
    ├── models/                     # 데이터 모델
    ├── utils/                      # 유틸리티
    └── config/                     # 설정 관리
```

## 🎯 **Pipeline-oriented의 장점**

### **1. 확장성**
- 각 Step을 독립적으로 스케일링
- 새로운 Pipeline 쉽게 추가
- 병렬 처리 최적화

### **2. 유지보수성**
- 단일 책임 원칙 (각 Step이 하나의 기능)
- 독립적인 테스트 가능
- 장애 격리 및 복구 용이

### **3. 모니터링**
- 각 Step별 성능 측정
- 병목 지점 명확한 식별
- 실시간 파이프라인 상태 추적

### **4. 재사용성**
- Step들을 다른 Pipeline에서 재사용
- 공통 로직의 중앙화
- 템플릿 기반 워크플로우

## 🔧 **Argo Workflows 통합**

### **워크플로우 예시**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: conversation-processing
spec:
  entrypoint: conversation-pipeline
  templates:
  - name: conversation-pipeline
    dag:
      tasks:
      - name: validate-input
        template: validation-step
      - name: load-context
        template: context-step
        dependencies: [validate-input]
      - name: process-llm
        template: llm-step
        dependencies: [load-context]
      - name: build-response
        template: response-step
        dependencies: [process-llm]
```

## 🚀 **구현 전략**

### **Phase 1: Core Pipeline 구현**
1. 기본 Pipeline 인터페이스 정의
2. Conversation Pipeline 구현
3. Analysis Pipeline 구현

### **Phase 2: Argo Workflows 통합**
1. Workflow 템플릿 작성
2. K8s 환경 설정
3. 파이프라인 배포 자동화

### **Phase 3: 고급 기능**
1. 동적 파이프라인 생성
2. A/B 테스트 지원
3. 실시간 모니터링 대시보드

## 📊 **성능 최적화**

### **병렬 처리**
- 독립적인 Step들을 병렬 실행
- GPU 리소스 효율적 활용
- 배치 처리 최적화

### **캐싱 전략**
- Step 결과 캐싱
- 중간 결과 재사용
- 컨텍스트 캐싱

### **리소스 관리**
- Step별 리소스 요구사항 정의
- 동적 스케일링
- 비용 최적화
