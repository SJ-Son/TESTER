# Frontend Application

## 기술 스택

- **Vue 3** - Composition API
- **TypeScript** - 타입 안정성
- **Pinia** - 상태 관리
- **TailwindCSS** - 스타일링
- **Vite** - 빌드 도구
- **Playwright** - E2E 테스트

## 디렉토리 구조

```
src/
├── api/                 # API 통신 레이어
│   ├── auth.ts         # 인증 API
│   ├── generator.ts    # 테스트 생성 API (SSE)
│   └── types.ts        # API 타입 정의
│
├── components/          # 재사용 가능한 UI 컴포넌트
│   ├── CodeEditor.vue  # 코드 입력 에디터
│   ├── TestResult.vue  # 생성 결과 표시
│   ├── ControlPanel.vue # 언어/모델 선택 패널
│   ├── HistoryPanel.vue # 생성 히스토리
│   └── CookieConsent.vue # 쿠키 동의 배너
│
├── composables/         # Vue Composables (로직 재사용)
│   └── useTestGeneration.ts
│
├── stores/              # Pinia 상태 관리
│   └── testerStore.ts  # 전역 상태
│
├── views/               # 페이지 컴포넌트
│   ├── HomeView.vue    # 메인 페이지
│   ├── PrivacyPolicy.vue
│   ├── TermsOfService.vue
│   └── ChangelogView.vue
│
├── utils/               # 유틸리티 함수
│   ├── constants.ts    # 전역 상수
│   └── lazyLoad.ts     # 지연 로딩
│
├── router/              # Vue Router 설정
│   └── index.ts
│
└── App.vue              # 루트 컴포넌트
```

## 핵심 패턴

### 1. **Composition API**

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)

onMounted(() => {
  console.log('Component mounted')
})
</script>
```

### 2. **SSE (Server-Sent Events) 스트리밍**

```typescript
// api/generator.ts
const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  
  const chunk = decoder.decode(value)
  // 실시간으로 onChunk 콜백 호출
  if (line.startsWith('data:')) {
    const data = JSON.parse(line.slice(6))
    if (data.type === 'chunk') {
      onChunk(data.content)
    }
  }
}
```

### 3. **Pinia 상태 관리**

```typescript
// stores/testerStore.ts
export const useTesterStore = defineStore('tester', () => {
  // State
  const inputCode = ref('')
  const generatedCode = ref('')
  const isGenerating = ref(false)
  
  // Actions
  const generateTestCode = async (turnstileToken: string) => {
    isGenerating.value = true
    await generatorApi.generateTestCode(...)
    isGenerating.value = false
  }
  
  return { inputCode, generatedCode, isGenerating, generateTestCode }
})
```

### 4. **Composable 패턴**

```typescript
// composables/useTestGeneration.ts
export function useTestGeneration() {
  const isGenerating = ref(false)
  const result = ref('')
  
  const generate = async (options) => {
    isGenerating.value = true
    // 로직...
  }
  
  return { isGenerating, result, generate }
}
```

### 5. **반응형 UI (Mobile First)**

```vue
<!-- Desktop: 2-column grid -->
<div v-if="!isMobile" class="grid grid-cols-2">
  <CodeEditor />
  <TestResult />
</div>

<!-- Mobile: Tabbed view -->
<div v-else>
  <button @click="viewMode = 'edit'">EDIT</button>
  <button @click="viewMode = 'result'">RESULT</button>
  
  <CodeEditor v-if="viewMode === 'edit'" />
  <TestResult v-else />
</div>
```

## 주요 기능 구현

### Cloudflare Turnstile (Bot 방지)

```typescript
// HomeView.vue
const handleGenerate = async () => {
  // 1. Turnstile 스크립트 지연 로딩
  await loadTurnstile()
  
  // 2. Invisible 챌린지 생성
  const token = await new Promise<string>((resolve) => {
    const container = document.createElement('div')
    window.turnstile.render(container, {
      sitekey: import.meta.env.VITE_TURNSTILE_SITE_KEY,
      callback: (token) => resolve(token)
    })
  })
  
  // 3. 토큰과 함께 API 요청
  await store.generateTestCode(token)
}
```

### LocalStorage 히스토리 관리

```typescript
// stores/testerStore.ts
const addToHistory = (input, result, language) => {
  // 최대 10개 유지
  if (history.value.length >= MAX_HISTORY_ITEMS) {
    history.value.pop()
  }
  history.value.unshift({ input, result, language })
  
  localStorage.setItem('tester_history', JSON.stringify(history.value))
}
```

### 코드 하이라이팅

```vue
<!-- TestResult.vue -->
<highlightjs language="python" :code="generatedCode" />
```

## 개발 가이드

### 개발 서버 실행

```bash
npm install
npm run dev
# http://localhost:5173
```

### 빌드

```bash
npm run build
# dist/ 폴더에 생성
```

### E2E 테스트

```bash
npm run test:e2e
npm run test:e2e:ui  # UI 모드
```

### 린팅

```bash
npm run lint
```

## 환경 변수

```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=your_site_key
VITE_GOOGLE_CLIENT_ID=your_client_id
```

## 컴포넌트 가이드라인

### 1. **Props는 TypeScript로 정의**

```vue
<script setup lang="ts">
interface Props {
  code: string
  language: 'python' | 'javascript' | 'java'
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false
})
</script>
```

### 2. **Emit은 명시적으로 선언**

```vue
<script setup lang="ts">
const emit = defineEmits<{
  generate: []
  clear: []
}>()

const handleGenerate = () => {
  emit('generate')
}
</script>
```

### 3. **CSS는 Tailwind 우선, 필요시 Scoped**

```vue
<style scoped>
/* 커스텀 스크롤바 등 Tailwind로 안 되는 것만 */
::-webkit-scrollbar {
  width: 4px;
}
</style>
```

## 성능 최적화

### 1. **지연 로딩**

```typescript
// utils/lazyLoad.ts
export const loadTurnstile = () => {
  if (window.turnstile) return Promise.resolve()
  
  return new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
    script.onload = resolve
    document.head.appendChild(script)
  })
}
```

### 2. **청크 분할**

```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor': ['vue', 'pinia', 'vue-router'],
        'highlight': ['highlight.js']
      }
    }
  }
}
```

### 3. **debounce/throttle**

```typescript
import { debounce } from 'lodash'

const handleResize = debounce(() => {
  isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
}, 150)
```

## 접근성 (a11y)

```vue
<!-- aria-label 추가 -->
<button aria-label="Generate test code" @click="generate">
  <RefreshCcw />
</button>

<!-- 키보드 네비게이션 -->
<div tabindex="0" @keydown.enter="handleSelect">
```

## 트러블슈팅

### SSE 연결 끊김
→ `keep-alive` 헤더 확인, EventSource polyfill 고려

### Turnstile 로딩 실패
→ CSP 헤더에 `https://challenges.cloudflare.com` 추가

### 빌드 크기 큼
→ `vite-plugin-compression` 사용, tree-shaking 확인
