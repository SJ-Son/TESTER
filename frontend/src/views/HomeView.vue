<script setup lang="ts">
/**
 * 메인 홈 화면 컴포넌트.
 * 코드 에디터, 결과 패널, 사이드바를 레이아웃하고 반응형 상태를 관리합니다.
 */
import { useTesterStore } from '../stores/testerStore'
import { ref, onMounted } from 'vue'
import { RefreshCcw } from 'lucide-vue-next'
import ControlPanel from '../components/ControlPanel.vue'
import CodeEditor from '../components/CodeEditor.vue'
import TestResult from '../components/TestResult.vue'
import { loadTurnstile } from '../utils/lazyLoad'
import { MOBILE_BREAKPOINT, TURNSTILE_TIMEOUT_MS } from '../utils/constants'

const store = useTesterStore()
const turnstileToken = ref<string | null>(null)
let turnstileWidgetId: string | null = null

// 반응형 상태
const viewMode = ref<'edit' | 'result'>('edit')

const updateIsMobile = () => {
  store.isMobile = window.innerWidth < MOBILE_BREAKPOINT
}

onMounted(() => {
  store.loadHistory()
  window.addEventListener('resize', updateIsMobile)
  updateIsMobile()
})

/**
 * 테스트 코드 생성을 요청합니다.
 * Turnstile 검증을 수행하고 API를 호출합니다.
 */
const handleGenerate = async () => {
  try {
    const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY
    if (!siteKey) throw new Error('Turnstile Site Key가 설정되지 않았습니다')
    
    // Turnstile 최초 사용 시 지연 로드
    await loadTurnstile()
    
    // 보이지 않는 Turnstile 챌린지 생성
    const token = await new Promise<string>((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Turnstile 시간 초과')), TURNSTILE_TIMEOUT_MS)
      
      if (typeof window.turnstile === 'undefined') {
        reject(new Error('Turnstile이 로드되지 않았습니다'))
        return
      }
      
      // 임시 컨테이너 요소 생성
      const container = document.createElement('div')
      container.style.position = 'fixed'
      container.style.top = '-9999px'
      document.body.appendChild(container)
      
      try {
        turnstileWidgetId = window.turnstile.render(container, {
          sitekey: siteKey,
          callback: (token: string) => {
            clearTimeout(timeout)
            document.body.removeChild(container)
            resolve(token)
          },
          'error-callback': () => {
            clearTimeout(timeout)
            document.body.removeChild(container)
            reject(new Error('Turnstile 검증 실패'))
          },
        })
      } catch (error) {
        clearTimeout(timeout)
        document.body.removeChild(container)
        reject(error)
      }
    })

    await store.generateTestCode(token)
    // 모바일에서는 생성 시작 후 결과 뷰로 전환
    if (store.isMobile) {
      viewMode.value = 'result'
    }
  } catch (err: any) {
    store.error = err.message
  }
}
</script>

<template>
  <div class="flex h-[100dvh] bg-gray-950 text-gray-200 overflow-hidden font-sans selection:bg-blue-500/30">
    <!-- Sidebar / Drawer -->
    <div 
      v-if="store.isMobile"
      class="fixed inset-0 z-50 transition-opacity duration-300"
      :class="store.isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'"
    >
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="store.isSidebarOpen = false"></div>
      <div 
        class="absolute left-0 top-0 bottom-0 w-80 transform transition-transform duration-300 shadow-2xl"
        :class="store.isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <ControlPanel />
      </div>
    </div>
    <ControlPanel v-else />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col bg-gray-950 min-w-0">
      <!-- Top header -->
      <header class="h-16 border-b border-gray-800 px-4 md:px-8 flex items-center bg-gray-900/50 backdrop-blur-md sticky top-0 z-20 justify-between">
        <div class="flex items-center space-x-3 text-xs font-bold font-mono uppercase tracking-widest transition-all duration-300">
          <button 
            v-if="store.isMobile"
            @click="store.isSidebarOpen = true"
            class="p-2 -ml-2 text-gray-400 hover:text-white"
            aria-label="Open sidebar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span class="text-gray-300 hidden sm:inline">Runner</span>
          <span class="text-gray-500 hidden sm:inline">></span>
          <span class="text-blue-400 text-sm font-black">{{ store.selectedLanguage.toUpperCase() }}</span>
          
          <div v-if="store.isGenerating" class="ml-2 md:ml-4 flex items-center space-x-2 text-blue-500/60 animate-pulse">
            <RefreshCcw class="w-3 h-3 animate-spin" />
            <span class="text-[9px] lowercase italic">streaming...</span>
          </div>
        </div>

        <!-- Mobile View Toggle -->
        <div v-if="store.isMobile" class="flex bg-gray-800 p-1 rounded-lg border border-gray-700">
          <button 
            @click="viewMode = 'edit'"
            class="px-3 py-1 rounded-md text-[10px] font-bold transition-all"
            :class="viewMode === 'edit' ? 'bg-blue-600 text-white' : 'text-gray-400'"
          >
            EDIT
          </button>
          <button 
            @click="viewMode = 'result'"
            class="px-3 py-1 rounded-md text-[10px] font-bold transition-all relative"
            :class="viewMode === 'result' ? 'bg-blue-600 text-white' : 'text-gray-400'"
          >
            RESULT
            <div v-if="store.isGenerating" class="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-hidden">
        <!-- Desktop Grid -->
        <div v-if="!store.isMobile" class="h-full grid grid-cols-2 p-8 gap-8">
          <CodeEditor @generate="handleGenerate" />
          <TestResult />
        </div>
        
        <!-- Mobile Tabbed View -->
        <div v-else class="h-full p-4 pb-20 overflow-y-auto">
          <CodeEditor v-if="viewMode === 'edit'" @generate="handleGenerate" />
          <TestResult v-else />
        </div>
      </div>
    </main>
  </div>
</template>
