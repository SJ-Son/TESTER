# Frontend 학습 메모

Vue 3, TypeScript, Pinia 기반 프론트엔드 구조 정리.

## 구조 및 설계

### Component Driven Development
화면을 컴포넌트 단위로 쪼개서 개발.
- `components/`: 재사용 가능한 UI 컴포넌트 (CodeEditor, TestResult 등).
- `views`: 컴포넌트들을 조립한 완성된 페이지.
- `stores`: 전역 상태 관리 (Pinia).
- `composables`: 재사용 가능한 로직 (useTestGenerator 등).

### Reactivity (반응성)
- Vue 3 Composition API (`<script setup>`) 사용.
- `ref`, `reactive`로 선언된 데이터가 바뀌면, 이걸 쓰고 있는 템플릿도 알아서 바뀜.
- `TestResult`에서 결과값이 들어오면 화면이 자동으로 갱신되는 원리.

### Responsive Design
- **모바일 모드**: 768px 미만 화면에서 Edit/Result를 탭으로 전환.
- **데스크탑 모드**: 2분할 그리드로 코드 편집기와 결과를 동시에 표시.
- **Utility**: `MOBILE_BREAKPOINT` 상수 사용 (`utils/constants.ts`).

---

## 주요 로직

### 1. 전역 상태 관리 (Pinia)
- `stores/testerStore.ts`에 핵심 데이터 몰아넣음.
- **Auth Integration**: `supabase.auth`를 사용하여 로그인/로그아웃 및 세션 상태 동기화.
  - `signInWithOAuth`로 Google 로그인.
  - 세션 토큰을 자동으로 API 요청 헤더에 포함.
- **State**: 입력 코드, 생성된 테스트 코드, 옵션, User Session, **Weekly Usage Stats** (사용량/한도/잔여) 등.
- **Actions**: API 호출 후 State 업데이트하는 비즈니스 로직 포함 (`fetchUserStatus` 등).

### 2. SSE 스트리밍 처리
- `api/generator.ts` 참고.
- `EventSource` 사용해서 백엔드 연결.
- 데이터가 올 때마다(`onmessage`) 기존 문자열에 덧붙여서 타이핑 효과 구현.

### 3. Offline-First History
- **전략**: 히스토리를 `localStorage`에 저장하여 새로고침 후에도 유지.
- **동기화**: 로그인 시 서버에서 이력을 가져와 로컬과 병합.
- **저장**: 코드 생성 후 백그라운드로 서버에 저장 (`BackgroundTasks`).
- **장점**: 네트워크 실패 시에도 로컬 이력은 유지됨.

### 4. Turnstile (Bot Protection)
- 코드 생성 요청 시 Cloudflare Turnstile로 봇 방지.
- Lazy loading으로 첫 사용 시에만 스크립트 로드 (`utils/lazyLoad.ts`).
- invisible 모드로 사용자 개입 최소화.

### 5. Dark Mode (TailwindCSS)
- `html` 태그에 `dark` 클래스 유무로 전환.
- Tailwind 클래스에 `dark:bg-black` 같은 식으로 다크모드 전용 스타일 지정.

---

## 실행 방법

```bash
npm install
cp .env.example .env.local
```

### 3. Setup Environment Variables
Create `.env` file in `frontend` directory:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_TURNSTILE_SITE_KEY=your_turnstile_site_key
```

### 4. Supabase Auth Configuration (PKCE)
We use **PKCE Flow** for better security and cleaner URLs.
1.  Go to Supabase Dashboard > Authentication > URL Configuration.
2.  Add `http://localhost:5173/auth/callback` to **Redirect URLs**.
3.  Ensure your production callback URL is also added (e.g., `https://your-domain.com/auth/callback`).

```bash
# .env.local에 Supabase 설정 입력
npm run dev
```

빌드:
```bash
npm run build
```

E2E 테스트:
```bash
npx playwright test
```
