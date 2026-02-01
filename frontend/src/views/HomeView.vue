<script setup lang="ts">
import { useTesterStore } from '../stores/testerStore'
import { ref, onMounted } from 'vue'
import { RefreshCcw } from 'lucide-vue-next'
import ControlPanel from '../components/ControlPanel.vue'
import CodeEditor from '../components/CodeEditor.vue'
import TestResult from '../components/TestResult.vue'

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
      <header class="h-16 border-b border-gray-800 px-8 flex items-center bg-gray-900/50 backdrop-blur-md sticky top-0 z-20">
        <div class="flex items-center space-x-3 text-xs font-bold font-mono uppercase tracking-widest transition-all duration-300">
          <span class="text-gray-500">Runner</span>
          <span class="text-gray-700">></span>
          <span class="text-blue-400 text-sm">{{ store.selectedLanguage.toUpperCase() }}</span>
          
          <div v-if="store.isGenerating" class="ml-4 flex items-center space-x-2 text-blue-500/60 animate-pulse">
            <RefreshCcw class="w-3 h-3 animate-spin" />
            <span class="text-[9px] lowercase italic">streaming...</span>
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
