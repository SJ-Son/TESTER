<script setup lang="ts">
import { useTesterStore } from './stores/testerStore'
import { Info, X, Sparkles } from 'lucide-vue-next'
import ControlPanel from './components/ControlPanel.vue'
import CodeEditor from './components/CodeEditor.vue'
import TestResult from './components/TestResult.vue'

const store = useTesterStore()

const handleGenerate = async () => {
  try {
    const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY
    if (!siteKey) throw new Error('reCAPTCHA Site Key is not configured')
    
    // @ts-ignore
    const recaptchaToken = await new Promise<string>((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('reCAPTCHA timeout')), 8000)
      // @ts-ignore
      if (typeof grecaptcha === 'undefined') {
        reject(new Error('reCAPTCHA not loaded'))
        return
      }
      // @ts-ignore
      grecaptcha.ready(() => {
        // @ts-ignore
        grecaptcha.execute(siteKey, { action: 'generate' }).then((token: string) => {
           clearTimeout(timeout)
           resolve(token)
        }).catch(reject)
      })
    })

    await store.generateTestCode(recaptchaToken)
  } catch (err: any) {
    store.error = err.message
  }
}
</script>

<template>
  <div class="flex h-screen bg-[#0a0a0a] text-gray-200 font-sans selection:bg-blue-500/20 overflow-hidden relative">
    <!-- Subtle Background Gradient -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 right-0 w-[50%] h-[50%] bg-blue-500/5 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-0 left-0 w-[30%] h-[30%] bg-indigo-500/5 blur-[100px] rounded-full"></div>
    </div>

    <!-- Sidebar -->
    <ControlPanel />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col relative z-10 min-w-0">
      <header class="h-14 border-b border-gray-800/60 flex items-center justify-between px-8 bg-black/10 backdrop-blur-sm">
        <div class="flex items-center space-x-2">
          <span class="text-[9px] font-bold text-gray-500 uppercase tracking-[0.2em]">Platform</span>
          <span class="text-gray-800">/</span>
          <span class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em]">Test Generator</span>
          <span class="text-gray-800">/</span>
          <span class="text-[10px] font-black text-blue-500 uppercase tracking-widest">{{ store.selectedLanguage }}</span>
        </div>
      </header>

      <div class="flex-1 grid grid-cols-2 p-6 gap-6 overflow-hidden">
        <!-- Editor Column -->
        <div class="flex flex-col h-full bg-[#111111]/40 rounded-2xl border border-gray-800/50 shadow-sm overflow-hidden">
          <CodeEditor @generate="handleGenerate" />
        </div>
        <!-- Result Column -->
        <div class="flex flex-col h-full bg-[#111111]/40 rounded-2xl border border-gray-800/50 shadow-sm overflow-hidden">
          <TestResult />
        </div>
      </div>
      
      <!-- Error Toast -->
      <Transition name="slide-up">
        <div v-if="store.error" class="absolute bottom-6 right-6 bg-gray-900 border border-red-500/30 px-5 py-3 rounded-xl flex items-center space-x-3 shadow-xl z-50">
          <Info class="w-4 h-4 text-red-500" />
          <span class="text-xs text-gray-300 font-medium">{{ store.error }}</span>
          <button @click="store.error = null" class="ml-2 text-gray-500 hover:text-white transition-colors">
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
      </Transition>
    </main>
  </div>
</template>

<style>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.1);
}

pre {
  background: transparent !important;
  padding: 0 !important;
}
code {
  background: transparent !important;
}
</style>
