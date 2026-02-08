<script setup lang="ts">
import { useTesterStore } from '../stores/testerStore'
import { Languages, Send, RefreshCcw, ShieldCheck } from 'lucide-vue-next'
import type { SupportedLanguage } from '../types'

const store = useTesterStore()

const emit = defineEmits(['generate'])

const supportedLanguages: { id: SupportedLanguage, label: string, name: string }[] = [
  { id: 'python', label: 'PY', name: 'Python' },
  { id: 'javascript', label: 'JS', name: 'JavaScript' },
  { id: 'java', label: 'JAVA', name: 'Java' }
]

const handleGenerate = () => {
  emit('generate')
}
</script>

<template>
  <section class="flex flex-col space-y-4 h-full">
    <div class="flex items-center justify-between h-9 mb-2 md:mb-0">
      <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
        <Languages class="w-4 h-4 text-blue-400" />
        <span>Source Code</span>
      </h2>
      
      <div class="flex items-center bg-gray-900 border border-gray-800 p-0.5 rounded-lg">
        <button 
          v-for="lang in supportedLanguages" 
          :key="lang.id"
          @click="store.selectedLanguage = lang.id"
          class="px-2 py-1 rounded-md text-[9px] font-black transition-all duration-200 tracking-tighter"
          :class="store.selectedLanguage === lang.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-gray-300'"
          :aria-label="'Select ' + lang.name"
        >
          {{ lang.label }}
        </button>
      </div>
    </div>
    
    <div class="flex-1 relative group">
      <div class="absolute -inset-0.5 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500"></div>
      <textarea
        v-model="store.inputCode"
        placeholder="Paste your source code here..."
        class="relative w-full h-full bg-gray-900/80 backdrop-blur-sm border border-gray-800 p-4 md:p-6 rounded-2xl outline-none focus:border-blue-500/50 transition-all text-sm font-mono text-gray-300 resize-none custom-scrollbar focus:ring-1 focus:ring-blue-500/20"
        aria-label="Source code input"
      ></textarea>
      
      <button 
        @click="handleGenerate"
        :disabled="store.isGenerating || !store.inputCode.trim()"
        class="absolute bottom-4 right-4 md:bottom-6 md:right-6 px-5 py-2.5 md:px-6 md:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-800 disabled:to-gray-800 disabled:text-gray-600 text-white rounded-xl shadow-xl shadow-blue-900/20 transition-all flex items-center space-x-2 group-focus-within:scale-105 active:scale-95 z-20 border border-white/10"
      >
        <Send v-if="!store.isGenerating" class="w-4 h-4" />
        <RefreshCcw v-else class="w-4 h-4 animate-spin" />
        <span class="font-bold text-xs md:text-base">{{ store.isGenerating ? (store.isMobile ? 'Wait' : 'Thinking...') : (store.isLoggedIn ? 'Generate' : 'Login') }}</span>
      </button>
      
      <div v-if="!store.isLoggedIn" class="absolute inset-0 bg-gray-950/40 backdrop-blur-[2px] rounded-2xl flex items-center justify-center">
        <p class="text-xs font-medium text-white bg-blue-600 px-4 py-2 rounded-full shadow-xl">Please Login First</p>
      </div>
      
      <div class="absolute -bottom-6 inset-x-2 flex items-center justify-between">
        <div class="flex items-center space-x-1.5 text-[10px] text-gray-300">
          <ShieldCheck class="w-3 h-3 text-green-500 shrink-0" />
          <span class="truncate">입력하신 코드는 서버에 <strong>암호화되어 안전하게 보관됩니다</strong>.</span>
        </div>

        <p class="text-[9px] text-gray-400 font-medium shrink-0 ml-4">
          Limit: 5/min
        </p>
      </div>
    </div>
  </section>
</template>
