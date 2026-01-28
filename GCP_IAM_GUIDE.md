# GCP IAM & GitHub Secrets Setup Guide

To enable automated deployment, follow these steps to configure permissions and secrets.

## 1. Google Cloud IAM Setup

Execute these commands in your local terminal or Google Cloud Shell:

```bash
# 1. 환경 변수 설정
PROJECT_ID="gen-lang-client-0355642569"
SA_NAME="github-actions-deployer"

# 2. 서비스 계정 생성
gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions Deployer"

# 3. 권한 부여 (IAM Roles)
# Artifact Registry 업로드 권한
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Cloud Run 배포 및 관리 권한
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.developer"

# 서비스 계정 대행 권한 (배포 시 필요)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# 4. 서비스 계정 키 생성 (JSON)
gcloud iam service-accounts keys create gcp-key.json \
    --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

## 2. GitHub Secrets 등록

1. GitHub 저장소의 **Settings > Secrets and variables > Actions** 메뉴로 이동합니다.
2. **New repository secret** 버튼을 눌러 다음 항목들을 추가합니다.

| Variable Name | Value | Note |
| :--- | :--- | :--- |
| `GCP_CREDENTIALS` | (gcp-key.json 파일의 전체 내용) | JSON 형식의 키 전체를 복사해서 붙여넣으세요. |
| `GEMINI_API_KEY` | (당신의 Gemini API Key) | 앱 실행에 필요한 API 키입니다. |
| `GCP_PROJECT_ID` | `gen-lang-client-0355642569` | GCP 프로젝트 ID입니다. |
| `GCP_REGION` | `asia-northeast3` | 배포 지역 (서울)입니다. |

> [!CAUTION]
> 생성된 `gcp-key.json` 파일은 보안상 매우 중요합니다. GitHub Secrets에 등록한 후에는 반드시 로컬에서 삭제하세요.
