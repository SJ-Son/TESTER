<script setup lang="ts">
import { useTesterStore } from './stores/testerStore'
import { ref, onMounted } from 'vue'
import { RefreshCcw } from 'lucide-vue-next'
import ControlPanel from './components/ControlPanel.vue'
import CodeEditor from './components/CodeEditor.vue'
import TestResult from './components/TestResult.vue'

const store = useTesterStore()

onMounted(() => {
  store.loadHistory()
})

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
  <div class="flex h-screen bg-gray-950 text-gray-200 overflow-hidden font-sans selection:bg-blue-500/30">
    <!-- Sidebar -->
    <ControlPanel />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col bg-gray-950">
      <!-- Top header -->
      <header class="h-16 border-b border-gray-800 px-8 flex items-center justify-between bg-gray-900/50 backdrop-blur-md sticky top-0 z-20">
        <div class="flex items-center space-x-6">
          <div class="text-[10px] text-gray-500 font-mono tracking-widest uppercase">
            Language
          </div>
          <div class="flex bg-gray-950/50 p-1 rounded-lg border border-gray-800">
            <button 
              v-for="lang in [
                { id: 'python', name: 'Python' },
                { id: 'javascript', name: 'JS' },
                { id: 'java', name: 'Java' }
              ]" 
              :key="lang.id"
              @click="store.selectedLanguage = lang.id"
              class="px-3 py-1 rounded-md text-[11px] font-bold transition-all duration-200 uppercase tracking-tighter"
              :class="store.selectedLanguage === lang.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-gray-300'"
            >
              {{ lang.name }}
            </button>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <div v-if="store.isGenerating" class="flex items-center space-x-2 text-[10px] text-blue-400/80 font-medium">
            <RefreshCcw class="w-3 h-3 animate-spin" />
            <span class="tracking-tight">Streaming response...</span>
          </div>
          <div class="h-4 w-[1px] bg-gray-800 mx-2"></div>
          <div class="text-[10px] text-gray-400 font-mono uppercase">
            Runner > <span class="text-blue-400">{{ store.selectedLanguage.toUpperCase() }}</span>
          </div>
        </div>
      </header>

      <div class="flex-1 grid grid-cols-2 p-8 gap-8 overflow-hidden">
        <!-- Main Work Area -->
        <CodeEditor @generate="handleGenerate" />
        <TestResult />
      </div>
    </main>
  </div>
</template>

<style>
/* Global styles to match main branch */
:root {
  color-scheme: dark;
}

html, body {
  background-color: #030712; /* bg-gray-950 */
  color-scheme: dark;
}

/* Custom Scrollbar for all */
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
