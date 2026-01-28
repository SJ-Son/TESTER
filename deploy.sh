#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="gen-lang-client-0355642569"
SERVICE_NAME="tester"
REGION="asia-northeast3"
REPO_NAME="tester" # Artifact Registry repository name

if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo "❌ Error: Please set your PROJECT_ID in line 7 of deploy.sh"
    echo "You can find it by running: gcloud config get-value project"
    exit 1
fi

echo "🚀 Starting Unified Deployment (Vue + FastAPI)..."

# 0. Ensure Artifact Registry repository exists
echo "📝 Ensuring Artifact Registry repository '$REPO_NAME' exists..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for QA Tester" \
    || echo "Repository already exists or creation failed (skipping...)"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# 1. Build & Push using Cloud Build
echo "📦 Building and pushing image to Artifact Registry..."
gcloud builds submit --tag $IMAGE_URL .

# 2. Deploy to Cloud Run
echo "🌍 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080

echo "✅ Deployment Complete!"
