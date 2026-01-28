#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
APP_NAME="tester-app"
REGION="asia-northeast3" # Seoul Region
IMAGE_TAG="gcr.io/$PROJECT_ID/$APP_NAME"

echo "Using Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Check for API Key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable is not set."
    echo "Please export GEMINI_API_KEY='your_api_key' before running this script."
    exit 1
fi

echo "🚀 Building container image..."
gcloud builds submit --tag $IMAGE_TAG .

if [ $? -ne 0 ]; then
    echo "❌ Build failed."
    exit 1
fi

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $APP_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful! Check the URL above."
else
    echo "❌ Deployment failed."
    exit 1
fi
