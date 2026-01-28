# 🚀 Google Cloud Run Deployment Guide (Independent)

이 가이드는 GitHub 연동 없이, 로컬 환경에서 직접 **Google Cloud Run**으로 배포하 절차를 설명합니다.
리포지토리가 Private 상태여도 안전하게 배포할 수 있습니다.

## 📋 사전 요구 사항 (Prerequisites)

1.  **Google Cloud CLI (gcloud)** 설치
    - [Gcloud CLI 설치 가이드](https://cloud.google.com/sdk/docs/install)
2.  **Google Cloud Project** 생성 및 결제 계정 연결
3.  **API Key** 준비 (`GEMINI_API_KEY`)

---

## ⚙️ 초기 설정 (First Time Setup)

터미널에서 아래 명령어를 순서대로 실행하여 인증 및 프로젝트 설정을 완료하세요.

```bash
# 1. 구글 계정 로그인
gcloud auth login

# 2. 사용할 프로젝트 설정 (PROJECT_ID는 GCP 콘솔에서 확인)
gcloud config set project [YOUR_PROJECT_ID]

# 3. Cloud Build & Cloud Run API 활성화
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

---

## 🚀 배포하기 (Deploy)

코드를 수정하고 배포할 때마다 아래 **단 하나의 명령어**만 실행하면 됩니다.
스크립트(`deploy.sh`)가 빌드와 배포를 자동으로 수행합니다.

### 1. API 키 설정 (세션당 1회)
배포 스크립트가 로컬 환경 변수에서 키를 읽어 안전하게 Cloud Run에 주입합니다.
# ⚠️ 주의: 이 파일은 git에 커밋되므로, 실제 키를 여기에 적은 채로 저장하지 마세요!
# 터미널에 직접 복사해서 실행하거나, .zshrc 등에 등록하는 것을 권장합니다.
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### 2. 배포 스크립트 실행
```bash
# 실행 권한 부여 (최초 1회)
chmod +x deploy.sh

# 배포 시작
./deploy.sh
```

---

## ✅ 주요 포인트
- **보안**: `.env` 파일은 절대 업로드되지 않습니다. 대신 `deploy.sh` 실행 시 환경 변수로 주입(`--set-env-vars`)됩니다.
- **이미지**: 소스 코드는 Google Container Registry (`gcr.io/...`)에 비공개로 저장됩니다.
- **리전**: 서울 리전 (`asia-northeast3`)으로 자동 설정되어 있습니다.

## 🛠️ 문제 해결
- **권한 오류**: `gcloud auth login`을 다시 실행하세요.
- **API Key 오류**: `echo $GEMINI_API_KEY`로 키가 설정되어 있는지 확인하세요.
