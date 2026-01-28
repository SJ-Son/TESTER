# 🚀 배포 가이드 (Deployment Guide)

Cloud Run에 배포하기 위한 2단계 절차입니다.

## 1. Google Cloud CLI (`gcloud`) 설치

현재 `gcloud` 명령어가 설치되어 있지 않습니다. 아래 명령어로 설치해주세요.

```bash
# 설치 스크립트 실행
curl https://sdk.cloud.google.com | bash
```

> **설치 후 반드시 터미널을 껐다 켜거나, `source ~/.zshrc`를 입력해야 명령어가 인식됩니다.**

---

## 2. 초기 설정 (한 번만 하면 됨)

```bash
# 1. 로그인
gcloud auth login

# 2. 프로젝트 선택 (GCP 콘솔에 있는 프로젝트 ID 입력)
gcloud config set project [YOUR_PROJECT_ID]
```

---

## 3. 배포 하기

이제 언제든 아래 명령어로 배포할 수 있습니다.

```bash
# 1. API 키 설정 (보안을 위해 로컬 변수로 설정)
export GEMINI_API_KEY="여기에_실제_키_입력"

# 2. 배포 스크립트 실행
chmod +x deploy.sh
./deploy.sh
```

> **Tip:** 배포 중 `ZIP does not support timestamps before 1980` 에러가 발생하면, `deploy.sh`가 자동으로 파일 시간을 갱신하여 해결합니다.
