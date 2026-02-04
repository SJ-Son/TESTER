# Components

## 컴포넌트 목록

### 1. **CodeEditor.vue**
**역할:** 소스 코드 입력 에디터

**Props:** 없음 (Pinia store 사용)

**Emits:**
- `generate` - 생성 버튼 클릭 시

**주요 기능:**
- 코드 입력 (textarea)
- 언어 선택 (드롭다운에서 이동 예정)
- 생성 버튼

**사용 예시:**
```vue
<CodeEditor @generate="handleGenerate" />
```

---

### 2. **TestResult.vue**
**역할:** 생성된 테스트 코드 표시

**Props:** 없음 (Pinia store 사용)

**주요 기능:**
- 코드 하이라이팅 (highlight.js)
- 복사 버튼 (클립보드)
- 재생성 버튼
- 로딩 상태 표시

**코드 하이라이팅:**
```vue
<highlightjs 
  :language="store.selectedLanguage" 
  :code="store.generatedCode" 
/>
```

---

### 3. **ControlPanel.vue**
**역할:** 사이드바 제어 패널

**Props:** 없음

**주요 기능:**
- 언어 선택 (Python, JavaScript, Java)
- 모델 선택 (Gemini 2.0 Flash 등)
- 히스토리 표시
- Google 로그인/로그아웃

**반응형:**
- 데스크탑: 고정 사이드바
- 모바일: Drawer (슬라이드)

---

### 4. **HistoryPanel.vue**
**역할:** 생성 히스토리 카드 표시

**Props:**
```typescript
interface Props {
  items: HistoryItem[]
}
```

**Emits:**
- `restore: [item]` - 히스토리 복원

**사용 예시:**
```vue
<HistoryPanel 
  :items="store.history" 
  @restore="store.restoreHistory" 
/>
```

---

### 5. **CookieConsent.vue**
**역할:** 쿠키 동의 배너

**Props:** 없음

**주요 기능:**
- 첫 방문 시 배너 표시
- 동의/거부 버튼
- LocalStorage에 저장

**표시 조건:**
```typescript
const showBanner = ref(!localStorage.getItem('cookie_consent'))
```

---

## 컴포넌트 작성 가이드

### 1. **파일 구조**

```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed } from 'vue'
import { useTesterStore } from '@/stores/testerStore'

// 2. Props/Emits
interface Props {
  title: string
}
const props = defineProps<Props>()
const emit = defineEmits<{ submit: [value: string] }>()

// 3. Store/Composables
const store = useTesterStore()

// 4. Local state
const isOpen = ref(false)

// 5. Computed
const displayTitle = computed(() => props.title.toUpperCase())

// 6. Methods
const handleSubmit = () => {
  emit('submit', 'value')
}

// 7. Lifecycle
onMounted(() => {
  console.log('Mounted')
})
</script>

<template>
  <div>
    <!-- UI -->
  </div>
</template>

<style scoped>
/* 최소한의 커스텀 스타일 */
</style>
```

### 2. **Props Validation**

```vue
<script setup lang="ts">
interface Props {
  code: string
  language?: 'python' | 'javascript' | 'java'
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  language: 'python',
  maxLength: 100000
})
</script>
```

### 3. **Emit Type Safety**

```vue
<script setup lang="ts">
const emit = defineEmits<{
  update: [value: string]
  delete: []
  select: [id: number, options: SelectOptions]
}>()
</script>
```

### 4. **Slot 사용**

```vue
<template>
  <div class="card">
    <header>
      <slot name="header">Default Header</slot>
    </header>
    <main>
      <slot>Default Content</slot>
    </main>
  </div>
</template>
```

### 5. **v-model 커스텀**

```vue
<script setup lang="ts">
const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const updateValue = (e: Event) => {
  emit('update:modelValue', (e.target as HTMLInputElement).value)
}
</script>

<template>
  <input :value="modelValue" @input="updateValue" />
</template>

<!-- 사용: -->
<MyInput v-model="text" />
```

## Tailwind 스타일 가이드

### 색상 팔레트

```
배경: bg-gray-950, bg-gray-900, bg-gray-800
텍스트: text-gray-200, text-gray-400
강조: text-blue-400, bg-blue-600
테두리: border-gray-800, border-gray-700
```

### 반응형 브레이크포인트

```vue
<div class="
  p-4        <!-- 모바일 -->
  md:p-8     <!-- 태블릿 이상 -->
  lg:p-12    <!-- 데스크탑 -->
">
```

### 다크 모드 (기본)

```vue
<!-- 이미 다크 모드가 기본이므로 dark: 클래스 불필요 -->
<div class="bg-gray-900 text-gray-200">
```

## 접근성 체크리스트

- [ ] `aria-label` for icon buttons
- [ ] `alt` for images
- [ ] Keyboard navigation (Tab, Enter, Esc)
- [ ] Focus visible styles (`:focus-visible`)
- [ ] Semantic HTML (`<button>`, `<nav>`, `<header>`)

## 테스트 작성

```typescript
// components/__tests__/CodeEditor.spec.ts
import { mount } from '@vue/test-utils'
import CodeEditor from '../CodeEditor.vue'

describe('CodeEditor', () => {
  it('emits generate event on button click', async () => {
    const wrapper = mount(CodeEditor)
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('generate')).toBeTruthy()
  })
})
```

## 재사용 팁

### Composable로 추출

```typescript
// composables/useClipboard.ts
export function useClipboard() {
  const copy = async (text: string) => {
    await navigator.clipboard.writeText(text)
  }
  
  return { copy }
}

// 사용:
const { copy } = useClipboard()
```

### Slot으로 유연하게

```vue
<!-- 재사용 가능한 Modal -->
<Modal>
  <template #header>
    <h2>Custom Title</h2>
  </template>
  
  <p>Custom Content</p>
  
  <template #footer>
    <button>Custom Action</button>
  </template>
</Modal>
```
