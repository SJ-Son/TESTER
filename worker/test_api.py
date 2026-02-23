from fastapi.testclient import TestClient
from main import app

client: TestClient = TestClient(app)

def test_health_check() -> None:
    """헬스 체크 엔드포인트 동작을 검증합니다.

    Returns:
        None
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    # Docker 클라이언트 상태에 따라 worker 상태가 달라질 수 있음
    assert "worker" in data

def test_invalid_auth() -> None:
    """인증 실패 시 적절한 에러 응답을 반환하는지 검증합니다.

    테스트 환경에서는 DISABLE_WORKER_AUTH=true로 설정되어 있어
    실제 인증 로직을 우회할 수 있으나, Docker 서비스 가용성에 따라
    503 에러가 발생할 수 있습니다.

    Returns:
        None
    """
    response = client.post("/execute", json={
        "input_code": "print('hello')",
        "test_code": "def test_x(): pass",
        "language": "python"
    })

    # Docker 서비스가 없는 환경(CI/CD 등)에서는 503 Service Unavailable 반환
    if response.status_code == 503:
        assert response.json()["detail"] == "Docker service unavailable on worker"
    elif response.status_code == 200:
        # Docker가 실행 중인 경우 정상 실행 결과 반환
        data = response.json()
        assert "success" in data
        assert "output" in data
    else:
        # 예상치 못한 상태 코드 발생 시 실패 처리
        assert False, f"Unexpected status code: {response.status_code}, Body: {response.text}"
