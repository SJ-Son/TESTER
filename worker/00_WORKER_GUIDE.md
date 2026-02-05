# 🐳 Tester Worker Guide

이 문서는 Hybrid 아키텍처의 핵심인 **Tester Worker (GCE VM)**의 운영 및 관리를 위한 가이드입니다.

## 🏗 아키텍처 개요
*   **Role**: Docker 샌드박스 실행 전담 (Backend의 실행 요청 처리)
*   **Infrastructure**: Google Compute Engine (GCE)
*   **Instance Name**: `tester-worker`
*   **Zone**: `asia-northeast3-a`
*   **Machine Type**: `e2-small`

## 📂 디렉토리 구조 (VM 내부)
`/home/sonseongjun/worker/` 위치에 배포되어 있습니다. (실제 실행은 Docker 컨테이너 내부에서 일어납니다.)

## 🔑 보안 (Security)
*   **WORKER_AUTH_TOKEN**: 백엔드와 워커 간의 통신을 보호하는 비밀키입니다.
*   **보안 조치**:
    *   `setup.sh` (토큰 포함)는 배포 후 즉시 삭제되었습니다.
    *   Docker 컨테이너는 환경변수(`-e WORKER_AUTH_TOKEN=...`)로 토큰을 주입받아 실행 중입니다.
    *   외부 공격을 막기 위해 어플리케이션 레벨에서 `Authorization: Bearer` 헤더를 검증합니다.

## 🛠 관리 명령어 (SSH 접속 후)

### 1. 로그 확인 (디버깅)
```bash
# 실시간 로그 확인
sudo docker logs -f tester-worker
```

### 2. 컨테이너 상태 확인
```bash
sudo docker ps -a
```

### 3. 서비스 재시작
```bash
sudo docker restart tester-worker
```

### 4. 수동 재배포 (코드가 변경되었을 때)
만약 `worker/` 코드를 수정했다면, 로컬에서 `setup.sh` (예제 파일 참고하여 토큰 주입 필요)를 다시 실행하거나 수동으로 이미지를 빌드해야 합니다.

```bash
# 컨테이너 중지 및 삭제
sudo docker stop tester-worker && sudo docker rm tester-worker

# 이미지 재빌드
sudo docker build -t tester-worker .

# 다시 실행 (토큰 필요)
export WORKER_AUTH_TOKEN="YOUR_TOKEN"
sudo docker run -d --name tester-worker -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WORKER_AUTH_TOKEN=$WORKER_AUTH_TOKEN \
  --restart unless-stopped \
  tester-worker
```

## 🚨 문제 해결
*   **"Execution service unavailable"**: VM이 꺼져있거나, Docker 컨테이너가 죽었는지 확인하세요. (`docker ps`)
*   **"Authentication failed"**: Cloud Run과 Worker의 토큰이 일치하지 않는 경우입니다.
