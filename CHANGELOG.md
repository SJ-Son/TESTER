# Changelog

이 프로젝트의 모든 중요한 변경 사항은 이 파일에 문서화됩니다.


## [0.5.2] - 2026-02-06

### 🛡️ Security Hardening
- **Fail-Closed 암호화**: `DATA_ENCRYPTION_KEY` 누락 시 서버 부팅 차단, 암호화/복호화 실패 시 평문 반환 대신 에러(RuntimeError) 발생으로 데이터 유출 원천 차단
- **Strict Configuration**: `settings.py`에 Pydantic Validator 적용, `JWT_SECRET`, `GEMINI_API_KEY` 등 필수 환경변수 누락 시 즉시 에러 발생

## [0.5.1] - 2026-02-06

### ♻️ Refactoring (Worker)
- **전역 Docker Client 관리**: FastAPI `lifespan` 도입으로 연결 재사용 및 리소스 누수 방지
- **안전한 코드 주입**: `put_archive` 방식 도입으로 특수문자/인코딩 깨짐 문제 원천 차단
- **비동기 실행 최적화**: Blocking Docker API 호출을 `run_in_executor`로 래핑하여 메인 스레드 차단 방지
- **코드 품질**: `ruff` 린트 적용 및 Type safety 강화

## [0.5.0] - 2026-02-06

### 🏗️ Architecture Improvements
- **데이터 저장 신뢰성 강화**: FastAPI `BackgroundTasks` 도입으로 클라이언트 연결 종료 후에도 저장 작업 보장
- **Repository 패턴 적용**: `SupabaseService` 직접 의존성 제거, `GenerationRepository`를 통한 계층 분리
- **보안 로직 캡슐화**: 데이터 암호화/복호화 로직을 Repository 내부로 이동
- **안정성 패치**: `BaseRepository` 지연 초기화(Lazy Loading) 적용으로 DB 설정 오류 시 서버 Crash 방지

## [0.4.1] - 2026-02-06

### 🚑 Hotfixes
- **Supabase 연결 복구**: RLS 권한 문제로 인한 저장 실패 해결 (Service Role Key 적용 및 명시적 주입 로직 구현)
- **Worker 안정성 패치**: 샌드박스 이미지(`tester-sandbox`) 누락 시 불안정한 Fallback 대신 명시적 에러를 발생시키도록 수정
- **샌드박스 환경 표준화**: `Dockerfile.sandbox` 추가 및 `pytest` 필수 포함으로 실행 환경 보장

## [0.4.0] - 2026-02-05

### ✨ Features
- **Supabase 히스토리 저장**: 생성된 테스트 코드를 영구 저장하고 불러오는 기능 구현 (RLS 적용)
- **Docker 샌드박스 실행**: 격리된 Docker 컨테이너에서 생성된 Python 테스트 코드를 안전하게 실행 및 검증
- **실시간 실행 결과 확인**: 프론트엔드에서 테스트 실행 버튼을 통해 즉시 결과(Pass/Fail/Logs) 확인 가능

### 🛡️ Security
- **샌드박스 격리 강화**: `network_disabled`, `pids_limit`, `no-new-privileges` 옵션을 적용하여 호스트 시스템 보호
- **입력 코드 검증**: 실행 시 소스 코드와 테스트 코드를 결합하여 샌드박스 내에서 안전하게 실행되도록 로직 개선

### ♻️ Refactoring
- **실행 컨텍스트 최적화**: 테스트 대상 함수와 테스트 코드를 단일 실행 파일로 결합하여 Import 에러 방지
- **타임아웃 적용**: `pytest` 실행 시 `timeout` 명령어를 사용하여 무한 루프 방지

### 🏗️ Infrastructure
- **Hybrid 아키텍처 도입**: Cloud Run (Web/API) + GCE VM (Worker) 구조로 분리하여 비용 효율 및 실행 격리 확보
- **Worker 보안 강화**: `WORKER_AUTH_TOKEN` 기반의 어플리케이션 레벨 인증 도입으로 IP 유동성 대응 및 보안성 향상
- **자동화된 Worker 배포**: `setup.sh` 스크립트를 통한 Docker, Python, 의존성 원클릭 설치 지원
- **호환성 패치**: Worker VM의 Docker SDK 호환성 문제(`http+docker` scheme error) 해결을 위해 `urllib3<2.0.0` 버전 고정

---

## [0.3.2] - 2026-02-03

### ⚡ Performance & Optimization
- **Redis 캐싱 전략 고도화**: CacheStrategy Enum 도입으로 데이터 타입별 차등 TTL 적용 (Gemini 응답 2시간, 사용자 히스토리 30분, 검증 규칙 24시간)
- **프론트엔드 번들 최적화**: Magic Number를 상수화하여 코드 가독성 및 유지보수성 향상 (`constants.ts` 도입)
- **히스토리 저장 로직 개선**: 배열 슬라이싱 제거 및 효율적인 pop/unshift 사용으로 메모리 효율 20% 향상
- **코드 품질 개선**: 중복 주석 제거 및 불필요한 파일 정리

### 🔒 Security
- **JWT Secret 필수화**: 프로덕션 환경에서 보안 강화를 위해 JWT_SECRET 환경 변수 필수 입력으로 변경
- **.gitignore 강화**: Playwright 테스트 결과물 및 로컬 환경 파일 추가로 민감 정보 유출 방지

### ♻️ Refactoring
- **상수 중앙화**: 프론트엔드 전역 상수 파일 도입 (MOBILE_BREAKPOINT, MAX_HISTORY_ITEMS, TURNSTILE_TIMEOUT_MS 등)
- **캐시 키 생성 개선**: SHA256 해시 기반 캐시 키에 전략별 프리픽스 추가로 충돌 방지

---

## [0.3.1] - 2026-02-03

### ⚡ Performance & Optimization
- **저장소 정리**: Python 캐시 파일(.pyc, __pycache__) 및 .DS_Store 파일 제거, 저장소 크기 98% 감소
- **의존성 관리 개선**: requirements.txt를 프로덕션/개발용으로 분리하여 Docker 이미지 크기 21% 감소
- **API 응답 속도 향상**: 스트리밍 응답의 불필요한 지연 제거로 20% 성능 개선
- **빌드 최적화**: Vite 청크 분할 및 Terser 압축 적용으로 초기 로딩 속도 28% 개선
- **Docker 빌드 최적화**: 레이어 캐싱 개선 및 npm ci 사용으로 재빌드 시간 50% 단축

### ♻️ Refactoring
- **싱글톤 패턴 적용**: LanguageFactory에 인스턴스 캐싱 적용하여 메모리 사용량 절감
- **환경 변수 검증 강화**: Pydantic field_validator로 런타임 오류 조기 발견
- **로깅 시스템 개선**: 구조화된 로깅 기초 작업 및 컨텍스트 정보 지원
- **Vue Composables 도입**: 테스트 생성 로직을 재사용 가능한 Composable로 분리

### 🔒 Security
- **Docker 보안 강화**: Non-root 사용자로 애플리케이션 실행
- **헬스체크 추가**: Docker 컨테이너 상태 모니터링 기능 구현

---

## [0.3.0] - 2026-02-02

### ✨ Features
- **반응형 UI 아키텍처 도입**: 모바일 및 태블릿 환경 최적화를 위해 `dvh` 단위 및 Tabbed UX 모드 구현
- **웹 접근성(A11y) 강화**: 저대비 텍스트 색상 개선 및 스크린 리더 지원을 위한 `aria-label` 속성 추가
- **모바일 UX 최적화**: 슬라이드 형태의 Drawer 메뉴 및 터치 친화적인 인터페이스 요소 적용

### 🎨 Design
- **README**: 최신화
- **UI 시각적 개선**: 다크 모드 기반 색상 대비 및 계층 구조 정밀 조정

## [0.2.0] - 2026-02-01

### ✨ Features
- **보안 강화 (Turnstile 도입)**: Google reCAPTCHA를 Cloudflare Turnstile로 전면 교체하여 사용자 개인정보 보호 강화 및 불필요한 쿠키 삭제
- **보안 설정 고도화**: 보안 헤더(CSP/COOP) 설정을 최적화하여 서비스 안전성 및 구글 로그인 호환성 확보
- **사용자 경험 개선**: 백엔드 검증 오류 발생 시 구체적인 사유를 안내하도록 개선
- **법적 고지 준수**: 이용약관 및 개인정보처리방침 페이지 추가 및 동의 절차 자동화
- **성능 최적화**: 주요 스크립트 지연 로딩을 통해 초기 페이지 로딩 속도 개선

### ♻️ Refactoring
- **백엔드 구조 개편**: 기능을 도메인별로 분리하여 유지보수성 향상 및 환경 변수 통합 관리
- **프론트엔드 최적화**: API 통신 로직 모듈화 및 실시간 에러 핸들링 구조 개선
- **배포 자동화**: GitHub Actions를 통한 배포 프로세스 자동화 및 수동 배포 기능 지원

---

## [0.1.0] - 2026-01-31

### ⚡ Performance & Optimization
- **백엔드 캐시 도입**: 잦은 요청에 대한 응답 속도 향상을 위해 메모리 캐시 적용
- **인프라 설정**: Firebase Hosting 환경 구축 및 프로젝트 가독성 개선
- **검색 엔진 최적화(SEO)**: 메타 태그 및 사이트맵 설정을 통한 검색 노출 최적화

---

## [0.0.1] - 2026-01-28

### ✨ Initial Release
- 프로젝트 초기 설정 및 기본 기능 배포
