# Stage 1: Build Vue.js Frontend
FROM node:20-slim AS build-stage

WORKDIR /app/frontend

# 의존성 파일만 먼저 복사 (레이어 캐싱)
COPY frontend/package*.json ./

# 의존성 설치 (빌드에 devDependencies 필요)
RUN npm ci

# 소스 코드 복사
COPY frontend/ .
COPY CHANGELOG.md ../

# 빌드 인자
ARG VITE_TESTER_INTERNAL_SECRET
ARG VITE_GOOGLE_CLIENT_ID
ARG VITE_TURNSTILE_SITE_KEY

ENV VITE_TESTER_INTERNAL_SECRET=$VITE_TESTER_INTERNAL_SECRET
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID
ENV VITE_TURNSTILE_SITE_KEY=$VITE_TURNSTILE_SITE_KEY

# 프로덕션 빌드
RUN npm run build

# Stage 2: Serve with FastAPI Backend
FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 의존성 파일만 먼저 복사 (레이어 캐싱)
COPY backend/requirements.txt ./backend/

# Python 의존성 설치 (소스 코드 변경 시에도 캐시 유지)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# 백엔드 소스 코드 복사
COPY backend ./backend

# 빌드된 프론트엔드 복사
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# 포트 노출
EXPOSE 8080

# Non-root 사용자로 실행 (보안)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# FastAPI 서버 시작 (Cloud Run은 PORT 환경 변수를 동적으로 설정)
CMD uvicorn backend.src.main:app --host 0.0.0.0 --port ${PORT:-8080}
