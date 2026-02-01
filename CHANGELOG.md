# Changelog

이 프로젝트의 모든 중요한 변경 사항은 이 파일에 문서화됩니다.

## [Unreleased]

## [0.3.0] - 2026-02-01

### ✨ Features (기능 추가)
- **Cloudflare Turnstile**: Google reCAPTCHA v3를 Cloudflare Turnstile로 완전 대체
  - Invisible 모드 적용으로 사용자 경험 개선
  - 서드 파티 쿠키 31개 완전 제거
  - 개인정보 보호 대폭 강화 (GDPR/CCPA 준수)
- **Lazy Loading**: Turnstile 스크립트 지연 로딩 구현 (`frontend/src/utils/lazyLoad.ts`)
- **Backend Script**: PYTHONPATH 자동 설정 스타트업 스크립트 (`backend/start_server.sh`)

### ♻️ Refactoring (코드 구조 개선)
- **Backend API**: 
  - `verify_recaptcha()` → `verify_turnstile()` 함수 교체
  - `RecaptchaError` → `TurnstileError` 예외 클래스 명명 변경
  - API 엔드포인트 필드명 `recaptcha_token` → `turnstile_token` 변경
- **Backend Settings**:
  - 환경 변수 `RECAPTCHA_SECRET_KEY` → `TURNSTILE_SECRET_KEY` 변경
  - CSP 헤더에 Cloudflare 도메인 추가
- **Frontend Integration**:
  - reCAPTCHA lazy loading → Turnstile lazy loading 교체
  - 환경 변수 `VITE_RECAPTCHA_SITE_KEY` → `VITE_TURNSTILE_SITE_KEY` 변경
  - API 타입 및 Store 업데이트

### ⚡️ Performance (성능 최적화)
- **초기 로드 최적화**: ~175 KiB JavaScript 제거 (reCAPTCHA 스크립트)
- **Lazy Loading**: Turnstile 스크립트를 Generate 버튼 클릭 시에만 로딩
- **네트워크 최적화**: 초기 페이지 로드 시 서드 파티 요청 0개

### 🛡️ Security (보안)
- **Privacy**: 서드 파티 쿠키 31개 → 0개 (100% 제거)
- **API Protection**: 유효한 Turnstile 토큰 없이는 백엔드 API 호출 불가
- **Bot Detection**: Cloudflare Turnstile의 고급 봇 감지 기능 활용

### 📝 Documentation (문서)
- Turnstile 설정 가이드 완비
- 마이그레이션 문서 및 테스트 결과 문서화
- `.env.example` 파일 업데이트



## [0.2.1] - 2026-02-01

### ♻️ Refactoring (안정성 개선)
- **SSE Error Handling**: 구조화된 이벤트 스트림(`event: error`) 도입 및 명확한 에러 전달
- **Frontend API Layer**: Store 내 fetch 로직을 `src/api/` 모듈로 분리 (유지보수성 향상)
- **Exception Handling**: 포괄적 예외 처리 개선 및 구체적 에러 타입 도입

## [0.2.0] - 2026-02-01

### ♻️ Refactoring (코드 구조 개선)
- **Backend Structure**: `main.py`를 `api/v1/{auth, generator, health, deps}.py`로 도메인별 분리
- **Linting & Formatting**: `ruff` 및 `pre-commit` 훅 도입으로 코드 스타일 통일 및 자동화

## [0.1.2] - 2026-02-01

### ✨ Features (기능 추가)
- **Legal**: 이용약관(`/terms`) 및 개인정보처리방침(`/privacy`) 페이지 구현
- **Consent Flow**: 로그인 시 무마찰(Frictionless) 동의 UX 적용 ("계속 진행 시 동의로 간주")
- **Router**: `vue-router` 도입으로 페이지 라우팅 구조(SPA) 구축
- **Changelog Sync**: `CHANGELOG.md` 파일과 `/changelog` 페이지 자동 동기화 구현
- **Modal UX**: 법적 고지 및 체인지로그 페이지를 오버레이 모달 형태로 개선 (문맥 유지)
- **Performance**: `highlight.js` 코드 분할 및 Gzip 압축 적용 (초기 로딩 속도 개선)
- **SEO**: 메타 태그 최적화 및 `robots.txt`, `sitemap.xml` 생성 for Search Engine Indexing
- **Accessibility**: 텍스트 대비(Contrast) 개선 및 Form Label 연결로 WCAG 접근성 기준 준수



### 🛡️ Security & Trust (보안 및 신뢰)
- **Policy**: 개인정보처리방침에 '소스 코드 영구 저장 금지' 조항(제3조) 신설
- **UI**: 에디터 하단에 "코드는 저장되지 않음" 안내 문구(Shield Icon) 추가
- **Headers**: 보안 헤더(HSTS Preload, XFO, CSP) 적용으로 웹 취약점 방어 강화 (Trust & Safety)
- **Routing**: `robots.txt` 및 `sitemap.xml` 정적 파일 서빙 라우트 추가 (SEO 색인 오류 해결)
- **Polish**: 헤더 가독성 추가 개선 및 HSTS Preload 적용

## [0.1.1] - 2026-01-31

### ⚡️ Performance (성능 최적화)
- **Backend**: `In-Memory LRU Cache` 도입으로 중복 요청에 대한 응답 속도 및 API 비용 절감
- **Backend**: `GzipMiddleware` 적용으로 API 응답 페이로드 크기 약 70% 감소
- **Frontend**: `highlight.js` Lazy Loading(지연 로딩) 적용으로 초기 로딩 속도(FCP) 개선

## [0.1.0] - 2026-01-31

### ✨ Features (기능 추가)
- **Custom Domain**: 사용자 정의 도메인 매핑을 위한 Firebase Hosting 설정 추가

### 🐛 Fixes (버그 수정)
- **Deployment**: dist 디렉토리 누락 오류 수정 및 스테이징 Firebase 라우팅 보정
- **Cloud Run**: `firebase.json` 내 Cloud Run rewrites 설정 수정

### 📝 Documentation (문서)
- **README**: 가독성 개선, 이모지 제거 및 최신 프로젝트 구조/성능 최적화 사항 반영
- **Portfolio**: 최종 포트폴리오용 README 추가

### 👷 CI/CD (배포 및 인프라)
- **Automation**: 태그 생성 및 Firebase 배포 자동화
- **Workflow**: 메인 브랜치에서 직접 배포 트리거되도록 단순화
- **Firebase**: Firebase 프록시 작동을 위한 더미 index.html 제거

## [0.0.3] - 2026-01-30

### ✨ Features (기능 추가)
- **History Feature**: localStorage 및 Pinia를 활용한 최근 생성 기록 기능 구현
- **Minimalist Design**: 미니멀리스트 UI 디자인 도입 및 Vite 환경 개선

### ♻️ Refactor (리팩토링)
- **Cleanup**: 사용하지 않는 코드 및 의존성 제거
- **Tests**: 카오스 테스트 시나리오를 정식 테스트 스위트로 통합 및 레거시 정리
- **Optimization**: 오디트 결과를 반영한 성능 최적화 및 통합 (DRY, Dead Code 제거)
- **Structure**: 테스트 코드 구조화 (unit, integration, security 분리)
- **Security**: Cloud Run을 위한 최소 권한 서비스 계정 적용

## [0.0.2] - 2026-01-29

### ✨ Features (기능 추가)
- **UI/UX Refinement**: 헤더 언어 선택 및 사이드바 릴리스 노트 레이아웃 개선

### 🐛 Fixes (버그 수정)
- **UI Restoration**: 사이드바 UI를 오리지널 디자인과 일치하도록 복구
- **Google Login**: 구글 로그인 버튼 디자인 최적화 및 다크 테마 호환성 수정

## [0.0.1] - 2026-01-28

### ✨ Features (기능 추가)
- **Initial Release**: 프로젝트 초기 설정 및 배포

### 🐛 Fixes (버그 수정)
- **UI/UX**: 초기 UI 버그 수정 및 레이아웃 안정화
