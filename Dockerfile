# Stage 1: Build Vue.js Frontend
FROM node:20-slim AS build-stage

WORKDIR /app/frontend

# 의존성 파일만 먼저 복사 (레이어 캐싱)
# 의존성 파일만 먼저 복사 (레이어 캐싱)
COPY frontend/package*.json ./

# 의존성 설치 (빌드에 devDependencies 필요)
RUN npm ci

# 소스 코드 복사
COPY frontend/ .
COPY CHANGELOG.md /app/
COPY TERMS_OF_SERVICE.md /app/
COPY PRIVACY_POLICY.md /app/

# List files to verify copy
RUN ls -la /app/

# 빌드 인자
ARG VITE_TESTER_INTERNAL_SECRET
ARG VITE_TURNSTILE_SITE_KEY
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

ENV VITE_TESTER_INTERNAL_SECRET=$VITE_TESTER_INTERNAL_SECRET
ENV VITE_TURNSTILE_SITE_KEY=$VITE_TURNSTILE_SITE_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

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
COPY backend/pyproject.toml backend/poetry.lock ./backend/

# Poetry 설치 및 의존성 설치
RUN pip install poetry && \
    cd backend && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# 백엔드 소스 코드 복사
COPY backend ./backend

# 빌드된 프론트엔드 복사
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend
ENV PORT=8080

# 포트 노출
EXPOSE 8080

# FastAPI 서버 시작
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT
