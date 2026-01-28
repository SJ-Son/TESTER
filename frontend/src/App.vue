<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Code, Languages, Sparkles, AlertCircle, RefreshCcw, Send, CheckCircle2 } from 'lucide-vue-next'
import hljs from 'highlight.js'
import 'highlight.js/styles/tokyo-night-dark.css'

// --- State ---
const inputCode = ref('')
const selectedLanguage = ref('python')
const selectedModel = ref('gemini-3-flash-preview')
const useReflection = ref(false)
const generatedCode = ref('')
const isGenerating = ref(false)
const error = ref('')
const streamEnded = ref(false)

const languages = [
  { id: 'python', name: 'Python', icon: 'py' },
  { id: 'javascript', name: 'JavaScript', icon: 'js' },
  { id: 'java', name: 'Java', icon: 'java' }
]

const models = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3 Flash (Fast)' }
]

// --- Streaming Logic ---
const generateTestCode = async () => {
  if (!inputCode.value.trim()) return
  
  error.value = ''
  generatedCode.value = ''
  isGenerating.value = true
  streamEnded.value = false

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_code: inputCode.value,
        language: selectedLanguage.value,
        model: selectedModel.value,
        use_reflection: useReflection.value
      })
    })

    if (!response.ok) throw new Error('Failed to connect to server')
    
    const reader = response.body?.getReader()
    if (!reader) throw new Error('No stream available')

    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value, { stream: true })
      
      // Check for ERROR prefix from backend
      if (chunk.startsWith('ERROR:')) {
        error.value = chunk.replace('ERROR:', '').trim()
        break
      }
      
      generatedCode.value += chunk
    }
  } catch (err: any) {
    error.value = err.message
  } finally {
    isGenerating.value = false
    streamEnded.value = true
  }
}

// --- Highlighting ---
const codeBlock = ref<HTMLElement | null>(null)
watch(generatedCode, () => {
  if (codeBlock.value) {
    hljs.highlightElement(codeBlock.value)
  }
})

onMounted(() => {
  if (codeBlock.value) hljs.highlightElement(codeBlock.value)
})
</script>

<template>
  <div class="flex h-screen bg-gray-950 overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-80 border-r border-gray-800 bg-gray-900 flex flex-col p-6 space-y-8">
      <div class="flex items-center space-x-3 text-blue-400">
        <Sparkles class="w-8 h-8" />
        <h1 class="text-xl font-bold tracking-tight text-white">TESTER</h1>
      </div>

      <!-- Strategy Config -->
      <div class="space-y-6">
        <div>
          <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-3">Target Language</label>
          <div class="grid grid-cols-1 gap-2">
            <button 
              v-for="lang in languages" 
              :key="lang.id"
              @click="selectedLanguage = lang.id"
              class="flex items-center space-x-3 px-4 py-3 rounded-lg border transition-all duration-200"
              :class="selectedLanguage === lang.id ? 'bg-blue-600/10 border-blue-500/50 text-blue-400' : 'bg-transparent border-gray-800 text-gray-400 hover:border-gray-700'"
            >
              <Code class="w-4 h-4" />
              <span class="font-medium text-sm">{{ lang.name }}</span>
            </button>
          </div>
        </div>

        <div>
          <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-3">Model</label>
          <select 
            v-model="selectedModel"
            class="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none appearance-none cursor-pointer"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
        </div>

        <div class="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-800">
          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-200">Self-Correction</p>
            <p class="text-[10px] text-gray-500">2-Pass Reflection Mode</p>
          </div>
          <input 
            type="checkbox" 
            v-model="useReflection"
            class="w-5 h-5 rounded border-gray-700 bg-gray-900 text-blue-600 focus:ring-blue-500"
          >
        </div>
      </div>

      <div class="flex-1"></div>

      <!-- Status Footer -->
      <div class="pt-6 border-t border-gray-800">
         <div class="flex items-center space-x-2 text-[10px] text-gray-500">
           <div class="w-2 h-2 rounded-full" :class="isGenerating ? 'bg-green-500 animate-pulse' : 'bg-gray-700'"></div>
           <span>{{ isGenerating ? 'System Active' : 'System Idle' }}</span>
         </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col bg-gray-950">
      <!-- Top header -->
      <header class="h-16 border-b border-gray-800 px-8 flex items-center justify-between">
        <div class="text-xs text-gray-400 font-mono">
          TEST RUNNER > <span class="text-blue-400">{{ selectedLanguage.toUpperCase() }}</span>
        </div>
        <div v-if="isGenerating" class="flex items-center space-x-2 text-xs text-blue-400/80">
          <RefreshCcw class="w-3 h-3 animate-spin" />
          <span>Streaming response...</span>
        </div>
      </header>

      <div class="flex-1 grid grid-cols-2 p-8 gap-8 overflow-hidden">
        <!-- Input Section -->
        <section class="flex flex-col space-y-4">
          <div class="flex items-center justify-between">
             <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
               <Languages class="w-4 h-4" />
               <span>Source Code</span>
             </h2>
          </div>
          <div class="flex-1 relative group">
            <textarea
              v-model="inputCode"
              placeholder="Paste your source code here..."
              class="w-full h-full bg-gray-900 border border-gray-800 p-6 rounded-2xl outline-none focus:border-blue-500/50 transition-colors text-sm font-mono text-gray-300 resize-none custom-scrollbar"
            ></textarea>
            <button 
              @click="generateTestCode"
              :disabled="isGenerating || !inputCode.trim()"
              class="absolute bottom-6 right-6 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-xl shadow-2xl shadow-blue-900/20 transition-all flex items-center space-x-2 group-focus-within:scale-105 active:scale-95"
            >
              <Send v-if="!isGenerating" class="w-4 h-4" />
              <RefreshCcw v-else class="w-4 h-4 animate-spin" />
              <span class="font-semibold">{{ isGenerating ? 'Thinking' : 'Generate' }}</span>
            </button>
          </div>
        </section>

        <!-- Output Section -->
        <section class="flex flex-col space-y-4 overflow-hidden">
          <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
            <CheckCircle2 class="w-4 h-4 text-green-500" />
            <span>Generated Quality Test Suite</span>
          </h2>
          
          <div v-if="error" class="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200 flex items-start space-x-4">
            <AlertCircle class="w-5 h-5 flex-shrink-0" />
            <div class="space-y-1">
              <p class="text-sm font-bold">Generation Error</p>
              <p class="text-xs opacity-80">{{ error }}</p>
            </div>
          </div>

          <div 
            class="flex-1 bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden flex flex-col"
            :class="{ 'animate-pulse border-blue-500/20': isGenerating && !generatedCode }"
          >
             <div class="bg-gray-800/50 px-6 py-3 border-b border-gray-800 flex items-center justify-between">
                <span class="text-[10px] font-mono text-gray-500 uppercase">{{ selectedLanguage }} suite</span>
                <span v-if="generatedCode" class="text-[10px] text-gray-400">Real-time rendering active</span>
             </div>
             <div class="flex-1 overflow-auto p-4 custom-scrollbar">
               <pre v-if="generatedCode" class="m-0"><code ref="codeBlock" :class="'language-' + selectedLanguage">{{ generatedCode }}</code></pre>
               <div v-else-if="!isGenerating" class="h-full flex flex-col items-center justify-center text-gray-600 space-y-3 opacity-30">
                 <Code class="w-12 h-12" />
                 <p class="text-xs font-medium">Ready for generation</p>
               </div>
             </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
pre {
  background: transparent !important;
  padding: 0 !important;
}
code {
  background: transparent !important;
}
</style>
