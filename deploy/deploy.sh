#!/bin/bash

# 실패 전파 + 안전한 IFS
set -euo pipefail
IFS=$'\n\t'

# 로그 파일로 이중 출력
exec > >(sudo tee -a /var/log/lifebookshelf-deploy.log) 2>&1
set -x

echo "====== Life Bookshelf AI v2 배포 시작..."

# docker compose 바이너리 선택 (신버전, 구버전)
if docker compose version >/dev/null 2>&1; then COMPOSE="docker compose"; else COMPOSE="docker-compose"; fi

# 0) 배포 잠금 - 동시 배포 방지
LOCK_FILE="/tmp/lifebookshelf-deploy.lock"
if [ -f "$LOCK_FILE" ]; then
  echo "Another deployment in progress. Waiting..."
  for i in {1..120}; do [ ! -f "$LOCK_FILE" ] && break; sleep 5; done
  [ -f "$LOCK_FILE" ] && rm -f "$LOCK_FILE" || true
fi
echo "$(date): Deployment started by $(whoami)" > "$LOCK_FILE"
cleanup(){ echo "Unlock"; rm -f "$LOCK_FILE"; }
trap cleanup EXIT

PROJECT_DIRECTORY="/home/ec2-user/deploy/zip"

# 0) ECR 로그인
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin 211125363878.dkr.ecr.ap-northeast-2.amazonaws.com

# 2) 새롭게 docker compose pull & 실행
cd "$PROJECT_DIRECTORY"

echo "===== Vector Database 디렉토리 확인..."
mkdir -p ./chroma_db ./logs
chmod 755 ./chroma_db ./logs

$COMPOSE up -d --pull always --force-recreate --remove-orphans

# 3) 불필요 리소스 청소(이 앱과 무관한 글로벌 dangling만)
# 1. 중지된 컨테이너 제거 (dangling)
docker container prune -f

# 2. 사용되지 않는 이미지 제거 (dangling)
docker image prune -f

# 3. 사용되지 않는 빌드 캐시 제거 (dangling)
docker builder prune -f >/dev/null 2>&1 || true

# 4) 헬스체크
echo "Checking nginx health..."
for i in {1..12}; do
  if curl -sf http://localhost/health; then
    echo "✅ nginx healthy"
    break
  fi
  echo "⏳ waiting nginx ($i/12)"; sleep 5
  if [ "$i" -eq 12 ]; then
    echo "❌ nginx failed health check after 60s"
    exit 1
  fi
done

echo "====== Deployment finished."