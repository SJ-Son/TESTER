<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Sparkles, User, LogOut, Code, Info, ChevronRight, History } from 'lucide-vue-next'
import HistoryPanel from './HistoryPanel.vue'
import * as authApi from '../api/auth'
import { loadGoogleSignIn } from '../utils/lazyLoad'

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
    const data = await authApi.loginWithGoogle(response.credential)
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

const initGoogleLogin = async () => {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    isSdkLoading.value = false
    return
  }

  try {
    // Lazy load Google Sign-In SDK
    await loadGoogleSignIn()
    
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
    }
  } catch (error) {
    console.error('Failed to load Google Sign-In:', error)
    isSdkLoading.value = false
  }
}

onMounted(() => {
  initGoogleLogin()
})
</script>

<template>
  <aside class="w-80 border-r border-gray-800 bg-gray-900 flex flex-col p-6 space-y-8 h-full relative z-10">
    <!-- Logo Section -->
    <div class="flex items-center space-x-3 text-blue-400 group cursor-default">
      <Sparkles class="w-8 h-8 transition-transform group-hover:scale-110" />
      <h1 class="text-xl font-bold tracking-tight text-white">TESTER</h1>
    </div>

    <!-- Auth Section -->
    <div class="space-y-4">
      <label class="text-xs font-semibold text-gray-400 uppercase tracking-widest block">Authentication</label>
      
      <div v-if="!store.isLoggedIn" class="relative group">
        <div v-if="isSdkLoading" class="w-full h-[40px] bg-gray-800 animate-pulse rounded-lg border border-gray-700"></div>
        <div id="google-login-btn" 
             class="w-full h-[40px] bg-gray-900 rounded-lg overflow-hidden transition-all duration-300" 
             :class="{ 'opacity-0': isSdkLoading, 'opacity-100': !isSdkLoading }">
        </div>
        
        <!-- Frictionless Consent Notice -->
        <p class="mt-3 text-[10px] text-gray-400 text-center leading-tight">
          계속 진행 시 
          <span class="text-blue-500/80 hover:text-blue-400 hover:underline cursor-pointer transition-colors" @click.stop.prevent="$router.push('/terms')">이용약관</span> 및 
          <span class="text-blue-500/80 hover:text-blue-400 hover:underline cursor-pointer transition-colors" @click.stop.prevent="$router.push('/privacy')">개인정보처리방침</span>에<br>
          동의하는 것으로 간주합니다.
        </p>
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
    <div class="space-y-6 flex-1 overflow-y-auto custom-scrollbar pr-1">

      <div>
        <label for="model-select" class="text-xs font-semibold text-gray-400 uppercase tracking-widest block mb-3">Model</label>
        <div class="relative group">
          <select 
            id="model-select"
            v-model="store.selectedModel"
            class="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none appearance-none cursor-pointer"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
          <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
            <ChevronRight class="w-4 h-4 rotate-90" />
          </div>
        </div>
      </div>

      <!-- History Section -->
      <HistoryPanel />
    </div>

    <!-- Status Footer -->
    <div class="pt-6 border-t border-gray-800 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2 text-[10px] text-gray-500">
          <div class="w-2 h-2 rounded-full" :class="store.isGenerating ? 'bg-green-500 animate-pulse' : 'bg-gray-700'"></div>
          <span>{{ store.isGenerating ? 'System Active' : 'System Idle' }}</span>
        </div>
      </div>
    </div>
    <!-- Footer -->
    <div class="pt-4 border-t border-gray-800/50 flex flex-col items-center space-y-2 pb-2">
      <div v-if="store.isLoggedIn" class="flex items-center space-x-2 text-[10px] text-gray-600">
        <router-link to="/terms" class="hover:text-blue-400 transition-colors">이용약관</router-link>
        <span>|</span>
        <router-link to="/privacy" class="hover:text-blue-400 transition-colors">개인정보처리방침</router-link>
      </div>
      <div class="text-[9px] text-gray-700 text-center font-mono">
        <router-link to="/changelog" class="hover:text-blue-500 transition-colors">v0.1.2</router-link> &copy; TESTER
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
