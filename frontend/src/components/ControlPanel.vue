<script setup lang="ts">
import { computed } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Sparkles, User, LogOut, ChevronRight, X } from 'lucide-vue-next'
import HistoryPanel from './HistoryPanel.vue'
import type { SupportedLanguage, GeminiModel } from '../types'
// @ts-ignore
import changelogRaw from '../../../CHANGELOG.md?raw'

const store = useTesterStore()

const currentVersion = computed(() => {
  const match = changelogRaw.match(/## \[(\d+\.\d+\.\d+)\]/)
  return match ? `v${match[1]}` : 'v0.3.0'
})

const languages: { id: SupportedLanguage, name: string, icon: string }[] = [
  { id: 'python', name: 'Python', icon: 'py' },
  { id: 'javascript', name: 'JavaScript', icon: 'js' },
  { id: 'java', name: 'Java', icon: 'java' }
]

const models: { id: GeminiModel, name: string }[] = [
  { id: 'gemini-3-flash-preview', name: 'Gemini 3 Flash (Fast)' }
]

const handleLogin = async () => {
  try {
    await store.loginWithGoogle()
  } catch (err: any) {
    store.error = 'Login failed: ' + err.message
  }
}

const logout = async () => {
  await store.logout()
}
</script>

<template>
  <aside class="w-80 border-r border-gray-800 bg-gray-900/50 backdrop-blur-xl flex flex-col p-6 space-y-8 h-full relative z-10">
    <!-- Logo Section -->
    <div class="flex items-center justify-between group cursor-default">
      <div class="flex items-center space-x-3">
        <div class="relative">
          <div class="absolute inset-0 bg-blue-500 blur-lg opacity-20 group-hover:opacity-40 transition-opacity"></div>
          <Sparkles class="w-8 h-8 text-blue-400 relative z-10 transition-transform group-hover:scale-110" />
        </div>
        <h1 class="text-xl font-bold tracking-tight text-white">TESTER</h1>
      </div>
      <!-- Mobile Close Button -->
      <button 
        v-if="store.isMobile"
        @click="store.isSidebarOpen = false"
        class="p-2 -mr-2 text-gray-500 hover:text-white lg:hidden"
        aria-label="Close sidebar"
      >
        <X class="w-6 h-6" />
      </button>
    </div>

    <!-- Auth Section -->
    <div class="space-y-4">
      <label class="text-xs font-semibold text-gray-400 uppercase tracking-widest block">Authentication</label>
      
      <div v-if="!store.isLoggedIn" class="relative group">
        <button
          @click="handleLogin"
          class="w-full h-10 bg-white hover:bg-gray-100 text-gray-900 font-semibold rounded-lg transition-all flex items-center justify-center space-x-2 shadow-lg shadow-white/5 active:scale-95"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.26.81-.58z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          <span class="text-sm">Login with Google</span>
        </button>
        
        <!-- Frictionless Consent Notice -->
        <p class="mt-3 text-[10px] text-gray-500 text-center leading-tight">
          계속 진행 시 
          <span class="text-blue-400 hover:text-blue-300 hover:underline cursor-pointer transition-colors" @click.stop.prevent="$router.push('/terms')">이용약관</span> 및 
          <span class="text-blue-400 hover:text-blue-300 hover:underline cursor-pointer transition-colors" @click.stop.prevent="$router.push('/privacy')">개인정보처리방침</span>에<br>
          동의하는 것으로 간주합니다.
        </p>
      </div>
      
      <div v-else class="flex flex-col space-y-3 p-3 bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20 rounded-xl">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <User class="w-4 h-4" />
            </div>
            <div>
              <div class="text-xs font-semibold text-white">Authenticated</div>
              <div class="text-[10px] text-blue-300/70">Ready to test</div>
            </div>
          </div>
          <button @click="logout" class="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-all" title="Logout" aria-label="Logout">
            <LogOut class="w-4 h-4" />
          </button>
        </div>
        
        <!-- Weekly Quota Display -->
        <div class="pt-2 border-t border-blue-500/10">
            <div class="flex justify-between items-center text-[10px] text-gray-400 mb-1">
                <span>Weekly Usage</span>
                <span :class="{'text-red-400': store.usageStats.remaining === 0, 'text-blue-400': store.usageStats.remaining > 0}">
                    {{ store.usageStats.weekly_usage }} / {{ store.usageStats.weekly_limit }}
                </span>
            </div>
            <div class="w-full bg-gray-700/50 rounded-full h-1.5 overflow-hidden">
                <div 
                    class="h-full rounded-full transition-all duration-500"
                    :class="store.usageStats.remaining === 0 ? 'bg-red-500' : 'bg-blue-500'"
                    :style="{ width: `${Math.min((store.usageStats.weekly_usage / store.usageStats.weekly_limit) * 100, 100)}%` }"
                ></div>
            </div>
            <div class="text-[9px] text-gray-500 mt-1 text-right">
                {{ store.usageStats.remaining }} requests remaining
            </div>
        </div>
      </div>
    </div>

    <!-- Strategy Config -->
    <div class="space-y-6 flex-1 overflow-y-auto custom-scrollbar pr-1">

      <div>
        <label for="model-select" class="text-xs font-semibold text-gray-300 uppercase tracking-widest block mb-3">Model</label>
        <div class="relative group">
          <select 
            id="model-select"
            v-model="store.selectedModel"
            class="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none appearance-none cursor-pointer"
          >
            <option v-for="m in models" :value="m.id">{{ m.name }}</option>
          </select>
          <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-300">
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
          <div class="w-2 h-2 rounded-full" :class="store.isGenerating ? 'bg-green-500 animate-pulse' : 'bg-gray-600'"></div>
          <span>{{ store.isGenerating ? 'System Active' : 'System Idle' }}</span>
        </div>
      </div>
    </div>
    <!-- Footer -->
    <div class="pt-4 border-t border-gray-800/50 flex flex-col items-center space-y-2 pb-2">
      <div v-if="store.isLoggedIn" class="flex items-center space-x-2 text-[10px] text-gray-400">
        <router-link to="/terms" class="hover:text-blue-400 transition-colors">이용약관</router-link>
        <span>|</span>
        <router-link to="/privacy" class="hover:text-blue-400 transition-colors">개인정보처리방침</router-link>
      </div>
      <div class="text-[9px] text-gray-400 text-center font-mono">
        <router-link to="/changelog" class="hover:text-blue-400 transition-colors uppercase tracking-widest">{{ currentVersion }}</router-link> &copy; TESTER
      </div>
    </div>
  </aside>
</template>

<style scoped>
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
</style>
