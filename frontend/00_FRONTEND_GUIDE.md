# Frontend 학습 메모

Vue 3, TypeScript, Pinia 기반 프론트엔드 구조 정리.

## 구조 및 설계

### Component Driven Development
화면을 컴포넌트 단위로 쪼개서 개발.
- `components/ui`: 버튼, 입력창 같은 순수 UI (재사용성 목적).
- `views`: 컴포넌트들을 조립한 완성된 페이지.
- `stores`: 전역 상태 관리.

### Reactivity (반응성)
- Vue 3 Composition API (`<script setup>`) 사용.
- `ref`, `reactive`로 선언된 데이터가 바뀌면, 이걸 쓰고 있는 템플릿도 알아서 바뀜.
- `ResultViewer`에서 결과값이 들어오면 화면이 자동으로 갱신되는 원리.

---

## 주요 로직

### 1. 전역 상태 관리 (Pinia)
- `stores/testerStore.ts`에 핵심 데이터 몰아넣음.
- **Auth Integration**: `supabase.auth` (`signInWithOAuth`) 사용하여 로그인 및 세션 관리.
  - **Token Handling**: API 호출 시 Supabase에서 발급받은 `Access Token`을 Authorization 헤더에 자동으로 실어서 보냄.
- State: 입력 코드, 생성된 테스트 코드, 옵션, User Session 등.
- Actions: API 호출 후 State 업데이트하는 비즈니스 로직 포함.

### 2. SSE 스트리밍 처리
- `api/generator.ts` 참고.
- `EventSource` 사용해서 백엔드 연결.
- 데이터가 올 때마다(`onmessage`) 기존 문자열에 덧붙여서 타이핑 효과 구현.

### 3. Dark Mode (TailwindCSS)
- `html` 태그에 `dark` 클래스 유무로 전환.
- Tailwind 클래스에 `dark:bg-black` 같은 식으로 다크모드 전용 스타일 지정.

---

## 실행 방법

```bash
npm install
npm run dev
```
