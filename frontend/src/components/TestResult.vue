<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Terminal, Copy, Check, Zap } from 'lucide-vue-next'
import hljs from 'highlight.js'
import debounce from 'lodash/debounce'

const store = useTesterStore()
const isCopied = ref(false)
const codeBlock = ref<HTMLElement | null>(null)

const highlightCode = debounce(() => {
  if (codeBlock.value) {
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

onMounted(() => {
  if (codeBlock.value && store.generatedCode) {
    // @ts-ignore
    hljs.highlightElement(codeBlock.value)
  }
})
</script>

<template>
  <section class="flex flex-col h-full overflow-hidden">
    <!-- Header Area -->
    <div class="h-12 border-b border-gray-800/50 flex items-center justify-between px-6 bg-gray-900/10">
      <div class="flex items-center space-x-2.5">
        <div class="p-1 px-2 rounded-md bg-blue-500/5 border border-blue-500/10">
          <Terminal class="w-3.5 h-3.5 text-blue-500" />
        </div>
        <span class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Test Suite</span>
      </div>
      
      <button 
        v-if="store.generatedCode"
        @click="copyToClipboard"
        class="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 transition-all text-[10px] font-bold text-gray-400 hover:text-white"
      >
        <component :is="isCopied ? Check : Copy" class="w-3 h-3" :class="{ 'text-blue-500': isCopied }" />
        <span>{{ isCopied ? 'Copied' : 'Copy All' }}</span>
      </button>
    </div>

    <!-- Content Area -->
    <div class="flex-1 relative overflow-auto custom-scrollbar">
      <!-- Empty State -->
      <Transition name="fade">
        <div v-if="!store.generatedCode && !store.isGenerating" class="absolute inset-0 flex flex-col items-center justify-center p-12 text-center select-none opacity-50">
          <div class="p-5 bg-gray-900/50 rounded-2xl border border-gray-800/50 mb-6">
            <Zap class="w-8 h-8 text-gray-700" />
          </div>
          <h3 class="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-2">Awaiting Analysis</h3>
          <p class="text-[10px] text-gray-600 max-w-[180px] leading-relaxed font-medium">
            Generated unit tests will appear here once the intelligence engine completes its cycle.
          </p>
        </div>
      </Transition>

      <div v-show="store.generatedCode || store.isGenerating" class="min-h-full font-mono text-[13px] leading-relaxed p-6 selection:bg-blue-500/10">
        <pre class="m-0"><code ref="codeBlock" :class="'language-' + store.selectedLanguage" class="hljs p-0 bg-transparent">{{ store.generatedCode }}<span v-if="store.isGenerating" class="inline-block w-1.5 h-3.5 bg-blue-500/50 animate-pulse ml-1 rounded-sm"></span></code></pre>
      </div>
    </div>
  </section>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.hljs {
  background: transparent !important;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

:deep(.hljs) {
  background: transparent !important;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 3px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
</style>
