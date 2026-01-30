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
  <div class="flex h-screen bg-gray-950 text-gray-200 overflow-hidden font-sans selection:bg-blue-500/30">
    <!-- Sidebar -->
    <ControlPanel />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col bg-gray-950">
      <!-- Top header -->
      <header class="h-16 border-b border-gray-800 px-8 flex items-center justify-between">
        <div class="text-xs text-gray-400 font-mono">
          TEST RUNNER > <span class="text-blue-400">{{ store.selectedLanguage.toUpperCase() }}</span>
        </div>
        <div v-if="store.isGenerating" class="flex items-center space-x-2 text-xs text-blue-400/80">
          <RefreshCcw class="w-3 h-3 animate-spin" />
          <span>Streaming response...</span>
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
html, body {
  background-color: #030712; /* bg-gray-950 */
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
