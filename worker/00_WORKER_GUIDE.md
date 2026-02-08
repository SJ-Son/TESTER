# Worker 운영 가이드

Hybrid 아키텍처의 핵심인 Worker VM 운영 및 관리 노트.

## 아키텍처 정보
- **Role**: Docker 샌드박스 실행 전담. Backend 요청 받아서 처리함.
- **Infra**: GCE (e2-small, asia-northeast3-a).
- **Instance**: `tester-worker`
- **위치**: `/home/sonseongjun/worker/` (여기서 Docker 실행)

## 보안 (Security)
- `WORKER_AUTH_TOKEN`: 백엔드 <-> 워커 통신용 비밀키.
- `Authorization: Bearer` 헤더로 토큰 검증함.
- `setup.sh`는 배포 직후 삭제해서 토큰 유출 방지.

## 주요 구현 사항 (v0.5.1 Refactor)

### 1. Docker Client Reuse
- **구현**: FastAPI `lifespan`으로 클라이언트를 전역 관리하여 리소스 효율화.
- **효과**: 매 요청마다 Docker 연결을 새로 만들지 않음. 성능 향상 + 메모리 누수 방지.

### 2. Safe Code Injection (put_archive)
- **문제**: 기존에는 `exec_create` + `exec_start`로 코드를 컨테이너에 전달했는데, 특수문자나 인코딩 문제로 실패하는 경우가 있었음.
- **해결**: `put_archive` 방식 도입. 
  - 코드를 tarball로 압축해서 컨테이너 내부에 파일로 전달.
  - binary-safe하여 어떤 문자든 안전하게 전달 가능.
- **코드 위치**: `worker/main.py`의 `execute_code` 함수 참고.

### 3. Async Execution
- **구현**: `run_in_executor`로 동기 Docker API를 비동기처럼 처리.
- **효과**: 메인 스레드 차단 방지. 여러 요청을 동시에 처리 가능.

### 4. Sandbox Security
Docker 컨테이너 실행 시 적용되는 보안 설정:
- `network_disabled=True`: 외부 네트워크 접근 차단.
- `pids_limit=50`: 프로세스 생성 제한 (fork bomb 방지).
- `mem_limit="256m"`: 메모리 제한.
- `cpu_quota=50000`: CPU 사용률 제한 (50%).
- `security_opt=["no-new-privileges"]`: 권한 상승 방지.

---

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

### 3. 샌드박스 이미지 확인
```bash
sudo docker images | grep tester-sandbox
```
- 이 이미지가 없으면 코드 실행이 실패함.
- Dockerfile.sandbox에 python, pytest 등 필요한 런타임이 포함되어 있음.

---

## 트러블슈팅

### "Execution service unavailable"
- **원인**: VM이 꺼졌거나 컨테이너가 죽음.
- **해결**: `sudo docker ps` 확인. 안 띄워져 있으면 위의 재배포 명령 실행.

### "Authentication failed"
- **원인**: 토큰 불일치.
- **해결**: `settings.py`의 `WORKER_AUTH_TOKEN`과 VM의 환경 변수가 같은지 확인.

### "Image tester-sandbox not found"
- **원인**: 샌드박스 이미지가 빌드되지 않음.
- **해결**: VM에 SSH 접속 후 `sudo docker build -t tester-sandbox -f Dockerfile.sandbox .` 실행.
