<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Code, CheckCircle2, AlertCircle, Copy, Check } from 'lucide-vue-next'
// import hljs from 'highlight.js' // Lazy loaded instead
import debounce from 'lodash/debounce'

const store = useTesterStore()
const isCopied = ref(false)
const codeBlock = ref<HTMLElement | null>(null)

const highlightCode = debounce(async () => {
  if (codeBlock.value) {
    const hljs = (await import('highlight.js')).default
    // @ts-ignore
    hljs.highlightElement(codeBlock.value)
  }
}, 150)

watch(() => store.generatedCode, () => {
  highlightCode()
})

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

onMounted(async () => {
  if (codeBlock.value && store.generatedCode) {
    const hljs = (await import('highlight.js')).default
    // @ts-ignore
    hljs.highlightElement(codeBlock.value)
  }
})
</script>

<template>
  <section class="flex flex-col space-y-4 h-full overflow-hidden">
    <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
      <CheckCircle2 class="w-4 h-4 text-green-500" />
      <span>Generated Quality Test Suite</span>
    </h2>
    
    <div v-if="store.error" class="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200 flex items-start space-x-4">
      <AlertCircle class="w-5 h-5 flex-shrink-0" />
      <div class="space-y-1">
        <p class="text-sm font-bold">Generation Error</p>
        <p class="text-xs opacity-80">{{ store.error }}</p>
      </div>
    </div>

    <div 
      class="flex-1 bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden flex flex-col"
      :class="{ 'animate-pulse border-blue-500/20': store.isGenerating && !store.generatedCode }"
    >
       <div class="bg-gray-800/50 px-6 py-3 border-b border-gray-800 flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-[10px] font-mono text-gray-500 uppercase">{{ store.selectedLanguage }} suite</span>
            <span v-if="store.generatedCode" class="text-[10px] text-gray-400">• Real-time rendering</span>
          </div>
          <button 
            v-if="store.generatedCode"
            @click="copyToClipboard"
            class="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all text-[10px] font-semibold"
            :class="{ 'text-green-400': isCopied }"
          >
            <component :is="isCopied ? Check : Copy" class="w-3 h-3" />
            <span>{{ isCopied ? 'Copied!' : 'Copy Code' }}</span>
          </button>
       </div>
       <div class="flex-1 overflow-auto p-4 custom-scrollbar">
         <pre v-if="store.generatedCode" class="m-0"><code ref="codeBlock" :class="'language-' + store.selectedLanguage" class="hljs">{{ store.generatedCode }}</code></pre>
         <div v-else-if="!store.isGenerating" class="h-full flex flex-col items-center justify-center text-gray-600 space-y-3 opacity-30">
           <Code class="w-12 h-12" />
           <p class="text-xs font-medium">Ready for generation</p>
         </div>
       </div>
    </div>
  </section>
</template>

<style scoped>
.hljs {
  background: transparent !important;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
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
