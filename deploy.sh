#!/bin/bash

# [설정]
APP_NAME="tester-app"
REGION="asia-northeast3" # 서울 리전
# 프로젝트 ID 자동 감지 (실패 시 직접 입력하세요)
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: gcloud 프로젝트가 설정되지 않았습니다."
    echo "'gcloud auth login' 및 'gcloud config set project [ID]'를 먼저 실행해주세요."
    exit 1
fi

echo "🔧 Fixing file timestamps (ZIP error prevention)..."
# gcloud 배포 시 "ZIP does not support timestamps before 1980" 오류 해결을 위해
# 모든 파일의 수정 시간을 현재 시간으로 갱신합니다.
find . -exec touch {} +

echo "🚀 Deploying to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# 1. 빌드 및 배포 (Cloud Build + Cloud Run)
gcloud run deploy $APP_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY

if [ $? -eq 0 ]; then
    echo "✅ 배포 성공! 위 URL에 접속해보세요."
else
    echo "❌ 배포 실패. 로그를 확인해주세요."
fi
