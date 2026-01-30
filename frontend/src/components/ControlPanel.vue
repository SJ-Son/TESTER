<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Sparkles, User, LogOut, Code, Info, ChevronRight } from 'lucide-vue-next'

const store = useTesterStore()
const isSdkLoading = ref(true)

const languages = [
  { id: 'python', name: 'Python', icon: 'py' },
  { id: 'javascript', name: 'JavaScript', icon: 'js' },
  { id: 'java', name: 'Java', icon: 'java' }
]

const models = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3 Flash (Fast)' }
]

const handleGoogleLogin = async (response: any) => {
  try {
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: response.credential })
    })
    
    if (!res.ok) throw new Error('Login failed')
    
    const data = await res.json()
    store.setToken(data.access_token)
  } catch (err: any) {
    store.error = '로그인에 실패했습니다: ' + err.message
  }
}

const logout = () => {
  store.clearToken()
  isSdkLoading.value = true
  setTimeout(initGoogleLogin, 100)
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
      callback: (res: any) => handleGoogleLogin(res),
      use_fedcm_for_prompt: false
    })
    // @ts-ignore
    google.accounts.id.renderButton(
      document.getElementById("google-login-btn"),
      { 
        theme: "filled_black", 
        size: "large", 
        width: 272,
        shape: "rectangular",
        logo_alignment: "left"
      }
    )
    isSdkLoading.value = false
  } else {
    setTimeout(initGoogleLogin, 100)
  }
}

onMounted(() => {
  initGoogleLogin()
})
</script>

<template>
  <aside class="w-80 border-r border-gray-800 bg-[#0f172a] flex flex-col p-8 space-y-10 h-full relative z-10">
    <!-- Logo Section -->
    <div class="flex items-center space-x-3 mb-4 group cursor-default">
      <div class="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-900/40 transition-transform group-hover:scale-105">
        <Sparkles class="w-6 h-6 text-white" />
      </div>
      <h1 class="text-xl font-black text-white tracking-widest">TESTER</h1>
    </div>

    <!-- Auth Section -->
    <div class="space-y-4">
      <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-1">Account</label>
      
      <div v-if="!store.isLoggedIn" class="relative">
        <div v-if="isSdkLoading" class="w-full h-[40px] bg-gray-800 animate-pulse rounded-lg border border-gray-700"></div>
        <div id="google-login-btn" class="w-full transition-opacity duration-300" :class="{ 'opacity-0': isSdkLoading, 'opacity-100': !isSdkLoading }"></div>
      </div>
      
      <div v-else class="flex items-center justify-between p-4 bg-blue-600/10 border border-blue-500/20 rounded-xl transition-all hover:bg-blue-600/15">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shadow-md">
            <User class="w-4 h-4" />
          </div>
          <span class="text-xs font-bold text-blue-100 italic tracking-tight">Signed In</span>
        </div>
        <button @click="logout" class="p-2 text-gray-400 hover:text-white transition-colors" title="Logout">
          <LogOut class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Strategy Config -->
    <div class="flex-1 space-y-8 overflow-y-auto custom-scrollbar pr-2">
      <div>
        <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-4">Target Strategy</label>
        <div class="grid grid-cols-1 gap-2">
          <button 
            v-for="lang in languages" 
            :key="lang.id"
            @click="store.selectedLanguage = lang.id"
            class="flex items-center space-x-3 px-4 py-3.5 rounded-xl border transition-all duration-200 group"
            :class="store.selectedLanguage === lang.id 
              ? 'bg-blue-600/15 border-blue-500/50 text-blue-400 shadow-inner' 
              : 'bg-transparent border-gray-800 text-gray-400 hover:border-gray-600 hover:text-gray-200'"
          >
            <Code class="w-4 h-4 transition-transform group-hover:scale-110" />
            <span class="font-bold text-sm tracking-tight">{{ lang.name }}</span>
          </button>
        </div>
      </div>

      <div>
        <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-4">Intelligence Engine</label>
        <div class="relative group">
          <select 
            v-model="store.selectedModel"
            class="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm font-semibold rounded-xl p-4 pr-10 focus:ring-2 focus:ring-blue-500/50 outline-none appearance-none cursor-pointer transition-all hover:border-gray-500"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
          <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500 group-hover:text-blue-400 transition-colors">
            <ChevronRight class="w-4 h-4 rotate-90" />
          </div>
        </div>
      </div>
    </div>

    <!-- Status Footer -->
    <div class="pt-6 border-t border-gray-800">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2 text-[10px] text-gray-500 font-bold uppercase tracking-wider">
          <div class="w-2 h-2 rounded-full" 
               :class="store.isGenerating ? 'bg-green-500 animate-pulse' : 'bg-gray-700'"></div>
          <span>{{ store.isGenerating ? 'System Active' : 'System Idle' }}</span>
        </div>
        <div class="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[9px] font-black text-blue-400 uppercase tracking-tighter">
          <Info class="w-2.5 h-2.5" />
          <span>5 REQ/MIN</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
#google-login-btn {
  color-scheme: dark !important;
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
</style>

<style scoped>
#google-login-btn {
  color-scheme: dark !important;
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
</style>
