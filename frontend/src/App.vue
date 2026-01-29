<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Code, Languages, Sparkles, AlertCircle, RefreshCcw, Send, CheckCircle2, Copy, Check, Info, LogOut, User } from 'lucide-vue-next'
import hljs from 'highlight.js'
import 'highlight.js/styles/tokyo-night-dark.css'

// --- State ---
const inputCode = ref('')
const selectedLanguage = ref('python')
const selectedModel = ref('gemini-3-flash-preview')
const generatedCode = ref('')
const isGenerating = ref(false)
const error = ref('')
const streamEnded = ref(false)
const isCopied = ref(false)
const userToken = ref(localStorage.getItem('tester_token') || '')
const userInfo = ref<any>(null)
const isLoggedIn = computed(() => !!userToken.value)
const isSdkLoading = ref(true)

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
  if (!inputCode.value.trim() || !isLoggedIn.value) return
  
  error.value = ''
  generatedCode.value = ''
  isGenerating.value = true
  streamEnded.value = false

  try {
    // 1. Get reCAPTCHA token
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

    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken.value}`
      },
      body: JSON.stringify({
        input_code: inputCode.value,
        language: selectedLanguage.value,
        model: selectedModel.value,
        recaptcha_token: recaptchaToken
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

// --- Copy Logic ---
const copyToClipboard = async () => {
  if (!generatedCode.value) return
  
  try {
    await navigator.clipboard.writeText(generatedCode.value)
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// --- Highlighting ---
const codeBlock = ref<HTMLElement | null>(null)
watch(generatedCode, () => {
  if (codeBlock.value) {
    hljs.highlightElement(codeBlock.value)
  }
})

// --- Auth Logic ---
const handleGoogleLogin = async (response: any) => {
  try {
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: response.credential })
    })
    
    if (!res.ok) throw new Error('Login failed')
    
    const data = await res.json()
    userToken.value = data.access_token
    localStorage.setItem('tester_token', data.access_token)
    // token에서 email 등 추출 가능하지만 생략
  } catch (err: any) {
    error.value = '로그인에 실패했습니다: ' + err.message
  }
}

const logout = () => {
  userToken.value = ''
  localStorage.removeItem('tester_token')
}

const initGoogleLogin = () => {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    isSdkLoading.value = false
    return
  }

  // @ts-ignore
  if (typeof google !== 'undefined' && google.accounts) {
    // @ts-ignore
    google.accounts.id.initialize({
      client_id: clientId,
      callback: handleGoogleLogin
    })
    // @ts-ignore
    google.accounts.id.renderButton(
      document.getElementById("google-login-btn"),
      { 
        theme: "filled_blue", 
        size: "large", 
        width: 272,
        shape: "rectangular",
        logo_alignment: "left"
      }
    )
    isSdkLoading.value = false
  } else {
    // Retry if script not yet available
    setTimeout(initGoogleLogin, 100)
  }
}

onMounted(() => {
  if (codeBlock.value) hljs.highlightElement(codeBlock.value)
  initGoogleLogin()
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

      <!-- Auth Section -->
      <div class="space-y-4">
        <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block">Authentication</label>
        <div v-if="!isLoggedIn">
          <div v-if="isSdkLoading" class="w-full h-[44px] bg-gray-800 animate-pulse rounded-lg border border-gray-700"></div>
          <div id="google-login-btn" class="w-full min-h-[44px] rounded-lg overflow-hidden transition-opacity duration-500" :class="{ 'opacity-0': isSdkLoading, 'opacity-100': !isSdkLoading }"></div>
        </div>
        <div v-else class="flex items-center justify-between p-4 bg-blue-600/10 border border-blue-500/20 rounded-xl">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white">
              <User class="w-4 h-4" />
            </div>
            <span class="text-xs font-medium text-blue-100 italic">Signed In</span>
          </div>
          <button @click="logout" class="p-2 text-gray-400 hover:text-white transition-colors" title="Logout">
            <LogOut class="w-4 h-4" />
          </button>
        </div>
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
      </div>

      <div class="flex-1"></div>

       <!-- Status Footer -->
      <div class="pt-6 border-t border-gray-800 space-y-4">
         <div class="flex items-center justify-between">
           <div class="flex items-center space-x-2 text-[10px] text-gray-500">
             <div class="w-2 h-2 rounded-full" :class="isGenerating ? 'bg-green-500 animate-pulse' : 'bg-gray-700'"></div>
             <span>{{ isGenerating ? 'System Active' : 'System Idle' }}</span>
           </div>
           <div class="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[9px] font-bold text-blue-400 uppercase tracking-tighter">
             <Info class="w-2.5 h-2.5" />
             <span>5 req/min</span>
           </div>
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
              class="absolute bottom-6 right-6 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-xl shadow-2xl shadow-blue-900/20 transition-all flex items-center space-x-2 group-focus-within:scale-105 active:95"
            >
               <Send v-if="!isGenerating" class="w-4 h-4" />
               <RefreshCcw v-else class="w-4 h-4 animate-spin" />
              <span class="font-semibold">{{ isGenerating ? 'Thinking...' : (isLoggedIn ? 'Generate' : 'Login to Start') }}</span>
            </button>
            <div v-if="!isLoggedIn" class="absolute inset-0 bg-gray-950/40 backdrop-blur-[2px] rounded-2xl flex items-center justify-center">
               <p class="text-xs font-medium text-white bg-blue-600 px-4 py-2 rounded-full shadow-xl">Please Login First</p>
            </div>
            <p class="absolute -bottom-6 right-2 text-[9px] text-gray-600 font-medium">
              Rate Limit: 5 requests / min per IP
            </p>
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
                <div class="flex items-center space-x-2">
                  <span class="text-[10px] font-mono text-gray-500 uppercase">{{ selectedLanguage }} suite</span>
                  <span v-if="generatedCode" class="text-[10px] text-gray-400">• Real-time rendering</span>
                </div>
                <button 
                  v-if="generatedCode"
                  @click="copyToClipboard"
                  class="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all text-[10px] font-semibold"
                  :class="{ 'text-green-400': isCopied }"
                >
                  <component :is="isCopied ? Check : Copy" class="w-3 h-3" />
                  <span>{{ isCopied ? 'Copied!' : 'Copy Code' }}</span>
                </button>
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
