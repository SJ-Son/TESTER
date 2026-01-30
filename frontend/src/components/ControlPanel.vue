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
        theme: "outline", 
        size: "medium", 
        width: 224, // Matches sidebar width better
        shape: "rectangular",
        logo_alignment: "left",
        text: "signin"
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
  <aside class="w-64 border-r border-gray-800/40 bg-[#080808] flex flex-col p-5 space-y-8 h-full relative z-10 transition-all duration-300">
    <!-- Logo Section -->
    <div class="flex items-center space-x-2.5 mb-2 group cursor-default px-1">
      <div class="p-1.5 bg-gray-900/50 rounded-md border border-gray-800/50">
        <Sparkles class="w-4 h-4 text-blue-500/80" />
      </div>
      <h1 class="text-sm font-bold text-gray-200 tracking-wide uppercase">Tester</h1>
    </div>

    <!-- Auth Section -->
    <div class="space-y-4">
      <div class="flex items-center justify-between px-1">
        <label class="text-[8px] font-bold text-gray-600 uppercase tracking-[0.2em]">Developer</label>
        <div v-if="store.isLoggedIn" class="w-1 h-1 rounded-full bg-blue-500 shadow-[0_0_5px_rgba(59,130,246,0.5)]"></div>
      </div>
      
      <div v-if="!store.isLoggedIn" class="px-1">
        <div v-if="isSdkLoading" class="w-full h-9 bg-gray-900/30 animate-pulse rounded-md border border-gray-800/30"></div>
        <div id="google-login-btn" class="w-full transition-opacity duration-500" :class="{ 'opacity-0': isSdkLoading, 'opacity-80 hover:opacity-100': !isSdkLoading }"></div>
      </div>
      
      <div v-else class="group relative p-2.5 bg-[#111111] border border-gray-800/40 rounded-xl hover:border-gray-700/60 transition-all duration-300">
        <button @click="logout" class="absolute top-2 right-2 p-1 rounded-md hover:bg-gray-800 text-gray-600 hover:text-gray-300 transition-colors">
          <LogOut class="w-2.5 h-2.5" />
        </button>
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center border border-gray-800 shadow-sm overflow-hidden">
            <User class="w-3.5 h-3.5 text-blue-500/60" />
          </div>
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-gray-300">Active</span>
            <span class="text-[8px] text-gray-600 font-bold uppercase tracking-tighter">Authorized</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Strategy Config -->
    <div class="flex-1 space-y-8 overflow-y-auto custom-scrollbar pr-1">
      <div>
        <label class="text-[8px] font-bold text-gray-600 uppercase tracking-[0.2em] block mb-4 px-1">Target Strategy</label>
        <div class="grid grid-cols-1 gap-1.5">
          <button 
            v-for="lang in languages" 
            :key="lang.id"
            @click="store.selectedLanguage = lang.id"
            class="group relative flex items-center justify-between px-3.5 py-2.5 rounded-lg border border-transparent transition-all duration-200"
            :class="store.selectedLanguage === lang.id 
              ? 'bg-[#151515] border-gray-800 text-blue-400' 
              : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900/40'"
          >
            <div class="flex items-center space-x-3 relative z-10">
              <Code class="w-3 h-3" :class="store.selectedLanguage === lang.id ? 'text-blue-500' : 'text-gray-700'" />
              <span class="font-bold text-[10px] tracking-tight uppercase">{{ lang.name }}</span>
            </div>
            <div v-if="store.selectedLanguage === lang.id" class="w-0.5 h-3 bg-blue-500 rounded-full"></div>
          </button>
        </div>
      </div>

      <div>
        <label class="text-[8px] font-bold text-gray-600 uppercase tracking-[0.2em] block mb-4 px-1">Engine</label>
        <div class="relative px-1">
          <select 
            v-model="store.selectedModel"
            class="w-full bg-[#111111] border border-gray-800/40 text-gray-400 text-[9px] font-bold uppercase rounded-lg p-2.5 pr-8 focus:ring-1 focus:ring-blue-500/20 outline-none appearance-none cursor-pointer transition-all"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
          <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-700">
            <ChevronRight class="w-3 h-3 rotate-90" />
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
