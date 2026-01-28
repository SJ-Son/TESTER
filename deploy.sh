#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="your-project-id" # Replace with your GCP Project ID
SERVICE_NAME="qa-test-generator-vue"
REGION="asia-northeast3" # Seoul

echo "🚀 Starting Unified Deployment (Vue + FastAPI)..."

# 1. Build Docker Image (Local/Cloud Build)
# We build from the root directory to access both /frontend and /backend
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# 2. Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080

echo "✅ Deployment Complete!"
