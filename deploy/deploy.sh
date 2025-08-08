#!/bin/bash

# Life Bookshelf AI v2 배포 스크립트

echo "====== Life Bookshelf AI v2 배포 시작..."

# 배포 디렉토리 생성
mkdir -p /home/ec2-user/deploy/zip
cd /home/ec2-user/deploy/zip/

echo "====== 기존 컨테이너 중지..."
docker-compose down

echo "====== ECR 로그인..."
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 211125363878.dkr.ecr.ap-northeast-2.amazonaws.com

echo "====== 최신 이미지 다운로드..."
docker-compose pull

echo "====== Vector Database 디렉토리 확인..."
mkdir -p ./chroma_db ./logs
chmod 755 ./chroma_db ./logs

echo "====== 서비스 시작..."
docker-compose up -d

echo "====== 서비스 시작 대기 (30초)..."
sleep 30

echo "====== 서비스 상태 확인..."
docker-compose ps

echo "====== Health Check..."
curl -f http://localhost/health || echo "❌ Health check 실패"
curl -f http://localhost:3001/health || echo "❌ AI 서버 health check 실패"

echo "====== Life Bookshelf AI v2 배포 완료!"