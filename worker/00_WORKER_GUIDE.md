# Tester Worker 메모

Hybrid 아키텍처의 핵심인 Worker VM 운영 및 관리 노트.

## 아키텍처 정보
- Role: Docker 샌드박스 실행 전담. Backend 요청 받아서 처리함.
- Infra: GCE (e2-small, asia-northeast3-a).
- Instance: `tester-worker`
- 위치: `/home/sonseongjun/worker/` (여기서 Docker 실행)

## 보안 (Security)
- `WORKER_AUTH_TOKEN`: 백엔드 <-> 워커 통신용 비밀키.
- `Authorization: Bearer` 헤더로 토큰 검증함.
- `setup.sh`는 배포 직후 삭제해서 토큰 유출 방지.

## 관리 명령어 (SSH)

### 1. 로그 확인
```bash
sudo docker logs -f tester-worker
```

### 2. 수동 재배포
코드가 바뀌었을 때 (자동 배포 실패 시).

```bash
# 기존 컨테이너 삭제
sudo docker stop tester-worker && sudo docker rm tester-worker

# 1. 샌드박스 이미지 빌드 (필수!)
# 이것이 없으면 테스트 실행 시 에러 발생함
sudo docker build -t tester-sandbox -f Dockerfile.sandbox .

# 2. 워커 이미지 빌드 & 실행
sudo docker build -t tester-worker .
export WORKER_AUTH_TOKEN="[토큰값]"
sudo docker run -d --name tester-worker -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WORKER_AUTH_TOKEN=$WORKER_AUTH_TOKEN \
  --restart unless-stopped \
  tester-worker
```

## 트러블슈팅
- "Execution service unavailable": VM이 꺼졌거나 컨테이너 죽음. `docker ps` 확인.
- "Authentication failed": 토큰 불일치. `settings.py`랑 VM 환경변수 대조 필요.
