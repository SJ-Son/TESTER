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
        shape: "pill",
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
  <aside class="w-72 border-r border-gray-800/60 bg-[#0d0d0d] flex flex-col p-6 space-y-8 h-full relative z-10">
    <!-- Logo Section -->
    <div class="flex items-center space-x-3 mb-2 group cursor-default">
      <div class="p-2 bg-gray-900 rounded-lg border border-gray-800">
        <Sparkles class="w-5 h-5 text-blue-500" />
      </div>
      <h1 class="text-lg font-bold text-white tracking-tight">TESTER</h1>
    </div>

    <!-- Auth Section -->
    <div class="space-y-4">
      <div class="flex items-center justify-between px-1">
        <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Identity</label>
        <div v-if="store.isLoggedIn" class="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
      </div>
      
      <div v-if="!store.isLoggedIn" class="relative">
        <div v-if="isSdkLoading" class="w-full h-[40px] bg-gray-900/50 animate-pulse rounded-lg border border-gray-800"></div>
        <div id="google-login-btn" class="w-full transition-opacity duration-300" :class="{ 'opacity-0': isSdkLoading, 'opacity-100': !isSdkLoading }"></div>
      </div>
      
      <div v-else class="group relative p-3 bg-gray-900/50 border border-gray-800 rounded-xl hover:border-gray-700 transition-colors">
        <button @click="logout" class="absolute top-2 right-2 p-1 rounded-md hover:bg-gray-800 text-gray-500 hover:text-white transition-colors">
          <LogOut class="w-3 h-3" />
        </button>
        <div class="flex items-center space-x-3">
          <div class="w-9 h-9 rounded-full bg-gray-800 flex items-center justify-center border border-gray-700">
            <User class="w-4 h-4 text-blue-500" />
          </div>
          <div class="flex flex-col">
            <span class="text-[11px] font-bold text-gray-200">Session Active</span>
            <span class="text-[9px] text-gray-600 font-medium tracking-tight">Developer Mode</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Strategy Config -->
    <div class="flex-1 space-y-8 overflow-y-auto custom-scrollbar pr-1">
      <div>
        <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-4 px-1">Target Strategy</label>
        <div class="grid grid-cols-1 gap-2">
          <button 
            v-for="lang in languages" 
            :key="lang.id"
            @click="store.selectedLanguage = lang.id"
            class="group relative flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-200"
            :class="store.selectedLanguage === lang.id 
              ? 'bg-blue-500/5 border-blue-500/40 text-blue-400' 
              : 'bg-transparent border-transparent text-gray-500 hover:text-gray-300 hover:bg-gray-900'"
          >
            <div class="flex items-center space-x-3 relative z-10">
              <Code class="w-3.5 h-3.5" :class="store.selectedLanguage === lang.id ? 'text-blue-500' : 'text-gray-600 group-hover:text-gray-500'" />
              <span class="font-bold text-[11px] tracking-tight">{{ lang.name }}</span>
            </div>
            <div v-if="store.selectedLanguage === lang.id" class="w-1 h-1 rounded-full bg-blue-500"></div>
          </button>
        </div>
      </div>

      <div>
        <label class="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-4 px-1">Intelligence</label>
        <div class="relative group">
          <select 
            v-model="store.selectedModel"
            class="w-full bg-gray-900 border border-gray-800 text-gray-300 text-[11px] font-bold rounded-xl p-3.5 pr-10 focus:ring-1 focus:ring-blue-500/40 outline-none appearance-none cursor-pointer transition-all"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
          <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
            <ChevronRight class="w-3.5 h-3.5 rotate-90" />
          </div>
        </div>
      </div>
    </div>

     <!-- Status Footer -->
     <div class="pt-6 border-t border-gray-800/60 pb-2">
       <div class="flex items-center justify-between px-1">
         <div class="flex items-center space-x-2">
           <div class="w-1.5 h-1.5 rounded-full" 
               :class="store.isGenerating ? 'bg-blue-500 animate-pulse' : 'bg-gray-700'"></div>
           <span class="text-[9px] font-bold text-gray-500 uppercase tracking-wider">{{ store.isGenerating ? 'Active' : 'Idle' }}</span>
         </div>
         <span class="text-[8px] font-bold text-gray-600 uppercase">5 REQ/MIN</span>
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
