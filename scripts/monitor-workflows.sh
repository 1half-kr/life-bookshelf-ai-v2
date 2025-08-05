#!/bin/bash

# Life Bookshelf AI v2 - Workflow Monitoring Script
# 실행: ./scripts/monitor-workflows.sh

set -e

echo "🔍 Life Bookshelf AI v2 - Workflow Monitoring"
echo "=============================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Argo Workflows 서버 상태 확인
echo -e "${BLUE}📊 Argo Workflows 서버 상태${NC}"
echo "----------------------------------------"
kubectl get pods -n argo | grep -E "(NAME|argo-workflows)"
echo ""

# 2. 네임스페이스 확인 및 생성
echo -e "${BLUE}🏗️  네임스페이스 확인${NC}"
echo "----------------------------------------"
if ! kubectl get namespace life-bookshelf-ai >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  life-bookshelf-ai 네임스페이스가 없습니다. 생성합니다...${NC}"
    kubectl create namespace life-bookshelf-ai
    kubectl label namespace life-bookshelf-ai app=life-bookshelf-ai
else
    echo -e "${GREEN}✅ life-bookshelf-ai 네임스페이스 존재${NC}"
fi
echo ""

# 3. 현재 실행 중인 워크플로우 확인
echo -e "${BLUE}🚀 현재 실행 중인 워크플로우${NC}"
echo "----------------------------------------"
RUNNING_WORKFLOWS=$(kubectl get workflows -n life-bookshelf-ai --no-headers 2>/dev/null | wc -l)
if [ "$RUNNING_WORKFLOWS" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  현재 실행 중인 워크플로우가 없습니다${NC}"
else
    kubectl get workflows -n life-bookshelf-ai
fi
echo ""

# 4. 워크플로우 템플릿 확인
echo -e "${BLUE}📋 워크플로우 템플릿 상태${NC}"
echo "----------------------------------------"
TEMPLATES=$(kubectl get workflowtemplates -n life-bookshelf-ai --no-headers 2>/dev/null | wc -l)
if [ "$TEMPLATES" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  워크플로우 템플릿이 배포되지 않았습니다${NC}"
    echo "템플릿 배포: kubectl apply -f workflows/templates/conversation-workflow.yaml"
else
    echo -e "${GREEN}✅ 워크플로우 템플릿 배포됨${NC}"
    kubectl get workflowtemplates -n life-bookshelf-ai
fi
echo ""

# 5. 최근 워크플로우 실행 이력 (argo CLI 사용)
echo -e "${BLUE}📈 최근 워크플로우 실행 이력${NC}"
echo "----------------------------------------"
if command -v argo >/dev/null 2>&1; then
    argo list -n life-bookshelf-ai --limit 5 2>/dev/null || echo -e "${YELLOW}⚠️  최근 실행 이력이 없습니다${NC}"
else
    echo -e "${YELLOW}⚠️  argo CLI가 설치되지 않았습니다${NC}"
    echo "설치: curl -sLO https://github.com/argoproj/argo-workflows/releases/latest/download/argo-darwin-amd64.gz"
fi
echo ""

# 6. 시스템 리소스 확인
echo -e "${BLUE}💻 시스템 리소스 사용량${NC}"
echo "----------------------------------------"
echo "Node 리소스:"
kubectl top nodes 2>/dev/null || echo -e "${YELLOW}⚠️  metrics-server가 설치되지 않았습니다${NC}"
echo ""
echo "Pod 리소스 (life-bookshelf-ai):"
kubectl top pods -n life-bookshelf-ai 2>/dev/null || echo -e "${YELLOW}⚠️  해당 네임스페이스에 실행 중인 Pod가 없습니다${NC}"
echo ""

# 7. 서비스 상태 확인
echo -e "${BLUE}🌐 서비스 상태 확인${NC}"
echo "----------------------------------------"
echo "FastAPI 서버 상태 확인:"
if curl -s http://localhost:3000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI 서버 정상 동작 (localhost:3000)${NC}"
    curl -s http://localhost:3000/health | jq '.' 2>/dev/null || echo "Health check OK"
else
    echo -e "${RED}❌ FastAPI 서버 연결 실패${NC}"
    echo "서버 시작: cd serve && python main_pipeline.py"
fi
echo ""

# 8. Redis 상태 확인
echo -e "${BLUE}🔴 Redis 상태 확인${NC}"
echo "----------------------------------------"
if redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis 서버 정상 동작${NC}"
    echo "Redis 정보:"
    redis-cli info server | grep -E "(redis_version|uptime_in_seconds)" || true
else
    echo -e "${RED}❌ Redis 서버 연결 실패${NC}"
    echo "Redis 시작: docker run -d -p 6379:6379 redis"
fi
echo ""

# 9. 모니터링 권장사항
echo -e "${BLUE}💡 모니터링 권장사항${NC}"
echo "----------------------------------------"
echo "1. Argo Workflows UI 접속: kubectl port-forward -n argo svc/argo-argo-workflows-server 2746:2746"
echo "2. 실시간 로그 확인: argo logs -n life-bookshelf-ai -f @latest"
echo "3. 워크플로우 테스트: curl -X POST http://localhost:3000/conversation/chat -H 'Content-Type: application/json' -d '{\"session_id\":\"test\",\"message\":\"안녕하세요\"}'"
echo "4. Grafana 대시보드 구성 (다음 단계)"
echo ""

echo -e "${GREEN}🎉 모니터링 스크립트 실행 완료!${NC}"
