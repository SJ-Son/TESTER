# Python 3.12 슬림 버전 사용 (용량 최적화)
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치를 위한 시스템 의존성 업데이트 (필요 시)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# Streamlit 포트 노출
EXPOSE 8501

# Healthcheck 설정 (컨테이너 상태 확인용)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 실행 명령어
# Streamlit은 8501 포트에서 실행되며 모든 IP(0.0.0.0)에서의 접근을 허용해야 함
ENTRYPOINT ["streamlit", "run", "run.py", "--server.port=8501", "--server.address=0.0.0.0"]
