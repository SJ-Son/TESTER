# Changelog

이 프로젝트의 모든 중요한 변경 사항은 이 파일에 문서화됩니다.

## [Unreleased]
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
