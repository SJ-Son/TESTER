<script setup lang="ts">
/**
 * 테스트 코드 생성 결과 표시 및 실행 컴포넌트.
 * 코드 하이라이팅, 복사, 실행 기능을 제공합니다.
 */
import { ref, watch, onMounted } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Code, CheckCircle2, AlertCircle, Copy, Check } from 'lucide-vue-next'
// import hljs from 'highlight.js' // 지연 로드됨
import debounce from 'lodash/debounce'

const store = useTesterStore()
const isCopied = ref(false)
const codeBlock = ref<HTMLElement | null>(null)

/**
 * 생성된 코드에 구문 강조(Syntax Highlight)를 적용합니다.
 * 성능을 위해 디바운스 처리되며, 언어 모듈을 동적으로 로드합니다.
 */
const highlightCode = debounce(async () => {
  if (codeBlock.value && store.selectedLanguage) {
    const hljs = (await import('highlight.js/lib/core')).default
    
    let langModule
    switch (store.selectedLanguage) {
      case 'python':
        langModule = await import('highlight.js/lib/languages/python')
        break
      case 'javascript':
        langModule = await import('highlight.js/lib/languages/javascript')
        break
      case 'java':
        langModule = await import('highlight.js/lib/languages/java')
        break
    }
    
    if (langModule) {
      hljs.registerLanguage(store.selectedLanguage, langModule.default)
    }
    
    // @ts-ignore
    hljs.highlightElement(codeBlock.value)
  }
}, 150)

// 코드가 변경되면 하이라이팅 재적용
watch(() => store.generatedCode, () => {
  highlightCode()
})

/** 생성된 코드를 클립보드에 복사합니다. */
const copyToClipboard = async () => {
  if (!store.generatedCode) return
  try {
    await navigator.clipboard.writeText(store.generatedCode)
    isCopied.value = true
    setTimeout(() => { isCopied.value = false }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// 컴포넌트 마운트 시 하이라이팅 적용
onMounted(async () => {
  if (codeBlock.value && store.generatedCode && store.selectedLanguage) {
    const hljs = (await import('highlight.js/lib/core')).default
    
    let langModule
    switch (store.selectedLanguage) {
      case 'python':
        langModule = await import('highlight.js/lib/languages/python')
        break
      case 'javascript':
        langModule = await import('highlight.js/lib/languages/javascript')
        break
      case 'java':
        langModule = await import('highlight.js/lib/languages/java')
        break
    }
    
    if (langModule) {
      hljs.registerLanguage(store.selectedLanguage, langModule.default)
    }

    // @ts-ignore
    hljs.highlightElement(codeBlock.value)
  }
})

const isExecuting = ref(false)
const executionResult = ref<{success: boolean, output: string, error: string} | null>(null)
const showOutput = ref(false)

/**
 * 생성된 테스트 코드를 실행(Worker에 요청)합니다.
 * 실행 중 상태를 관리하고 결과를 표시합니다.
 */
const runTest = async () => {
    if (!store.generatedCode) return
    isExecuting.value = true
    executionResult.value = null
    showOutput.value = true
    
    try {
        const result = await store.executeTest()
        executionResult.value = result
    } finally {
        isExecuting.value = false
    }
}
</script>

<template>
  <section class="flex flex-col space-y-4 h-full overflow-hidden">
    <div class="flex items-center h-9">
      <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
        <CheckCircle2 class="w-4 h-4 text-green-500" />
        <span>Generated Quality Test Suite</span>
      </h2>
    </div>
    
    <div v-if="store.error" class="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200 flex items-start space-x-4">
      <AlertCircle class="w-5 h-5 flex-shrink-0" />
      <div class="space-y-1">
        <p class="text-sm font-bold">Generation Error</p>
        <p class="text-xs opacity-80">{{ store.error }}</p>
      </div>
    </div>

    <div 
      class="flex-1 bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-2xl overflow-hidden flex flex-col min-h-[400px] shadow-2xl"
      :class="{ 'animate-pulse border-blue-500/30': store.isGenerating && !store.generatedCode }"
    >
       <div class="bg-gray-900/80 px-4 md:px-6 py-3 border-b border-gray-800 flex items-center justify-between sticky top-0 z-10 backdrop-blur-xl">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 rounded-full bg-red-500"></div>
            <div class="w-2 h-2 rounded-full bg-yellow-500"></div>
            <div class="w-2 h-2 rounded-full bg-green-500"></div>
            <span class="ml-2 text-[10px] font-mono text-gray-400 uppercase tracking-wider opacity-60">{{ store.selectedLanguage }} suite</span>
          </div>
          <div class="flex items-center space-x-2">
            <button 
                v-if="store.generatedCode && store.selectedLanguage === 'python'"
                @click="runTest"
                :disabled="isExecuting"
                class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 hover:text-white transition-all text-[10px] font-bold border border-white/5 shadow-lg disabled:opacity-50 backdrop-blur-sm"
              >
                <div v-if="isExecuting" class="animate-spin w-3 h-3 border-2 border-current border-t-transparent rounded-full"></div>
                <template v-else>
                    <component :is="Code" class="w-3 h-3" />
                    <span>Run</span>
                </template>
            </button>

            <button 
                v-if="store.generatedCode"
                @click="copyToClipboard"
                class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 hover:text-white transition-all text-[10px] font-bold border border-white/5 shadow-lg backdrop-blur-sm"
                :class="{ 'text-green-400 border-green-500/50 bg-green-900/20': isCopied }"
            >
                <component :is="isCopied ? Check : Copy" class="w-3 h-3" />
                <span>{{ isCopied ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
       </div>
       <div class="flex-1 overflow-auto p-6 custom-scrollbar bg-gray-950/30">
         <pre v-if="store.generatedCode" class="m-0"><code ref="codeBlock" :class="'language-' + store.selectedLanguage" class="hljs">{{ store.generatedCode }}</code></pre>
         <div v-else-if="!store.isGenerating" class="h-full flex flex-col items-center justify-center space-y-4 opacity-40">
           <div class="w-16 h-16 rounded-2xl bg-gray-800 flex items-center justify-center border border-gray-700 rotate-3">
             <Code class="w-8 h-8 text-gray-500" />
           </div>
           <p class="text-xs font-medium text-gray-500 uppercase tracking-widest">Ready to generate</p>
         </div>
       </div>

       <!-- Execution Result Console -->
       <div v-if="showOutput" class="border-t border-gray-800 bg-black/80 backdrop-blur p-4 h-1/3 overflow-auto transition-all duration-300 flex flex-col min-h-[150px]">
            <div class="flex justify-between items-center mb-2">
                <span class="text-xs font-mono font-bold text-gray-400">Execution Output</span>
                <button @click="showOutput = false" class="text-gray-500 hover:text-gray-300">✕</button>
            </div>
            
            <div v-if="isExecuting" class="text-gray-400 text-xs font-mono animate-pulse">Running tests in sandbox...</div>
            
            <div v-else-if="executionResult" class="font-mono text-xs whitespace-pre-wrap">
                <div v-if="!executionResult.success" class="text-red-400 mb-2 font-bold">Execution Failed</div>
                <div v-else class="text-green-400 mb-2 font-bold">Execution Successful</div>
                
                <div v-if="executionResult.error" class="text-red-300 bg-red-900/10 p-2 rounded mb-2">{{ executionResult.error }}</div>
                <div class="text-gray-300 max-w-full overflow-x-auto">{{ executionResult.output }}</div>
            </div>
       </div>
    </div>
  </section>
</template>

<style scoped>
.hljs {
  background: transparent !important;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: clamp(11px, 3vw, 13px);
  line-height: 1.6;
}

:deep(.hljs) {
  background: transparent !important;
}

pre {
  background: transparent !important;
  padding: 0 !important;
}
code {
  background: transparent !important;
}
</style>
