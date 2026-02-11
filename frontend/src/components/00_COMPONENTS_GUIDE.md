# Component 구조 메모

프론트엔드 UI 컴포넌트 설계 의도 및 역할 정리.

## 컴포넌트 목록

### CodeEditor
- 소스 코드 입력 에디터.
- **Props**: `modelValue` (양방향 바인딩), `language`, `placeholder` 등.
- **Emits**: `update:modelValue`, `generate` (생성 버튼 클릭 시).
- **특징**: Syntax highlighting 지원 (highlight.js).

### TestResult
- 생성된 테스트 코드 및 실행 결과 표시.
- **Props**: `code`, `isLoading`, `executionResult`.
- **기능**: 
  - 코드 복사 버튼
  - 실행 버튼
  - 성공/실패 여부에 따라 UI 변경 (테두리 색상, 아이콘)

### ControlPanel
- 사이드바 컨트롤 패널.
- **기능**:
  - 언어 선택 (Python, JavaScript, Java)
  - 모델 선택 (Gemini 1.5 Flash/Pro)
  - 로그인/로그아웃 버튼
  - **Weekly Quota**: 주간 사용량 및 잔여 횟수 Progress Bar 표시 (로그인 시).
  - 히스토리 패널 토글
- **반응형**: 데스크탑에서는 고정 사이드바, 모바일에서는 Drawer로 표시.

### HistoryPanel
- 생성 이력 목록 표시.
- **기능**:
  - 과거 생성한 코드 목록 보기
  - 클릭 시 해당 코드를 메인 에디터에 로드
  - 로컬 저장 + 서버 동기화 (Offline-First)

### CookieConsent
- 쿠키 동의 배너.
- **기능**: 첫 방문 시 약관 동의 받음.
- **저장**: 동의 여부를 `localStorage`에 저장.

---

## Data Flow (데이터 흐름 규칙)
1. **내려주기 (Props)**: 부모 -> 자식 데이터 전달.
2. **올려주기 (Emits)**: 자식 -> 부모 이벤트 전달 (클릭 등).
3. **전역 상태 (Pinia)**: 여러 컴포넌트가 공유해야 하는 데이터는 Store에서 관리.

단방향 데이터 흐름 원칙 지킬 것.
