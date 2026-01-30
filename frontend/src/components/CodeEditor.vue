<script setup lang="ts">
import { useTesterStore } from '../stores/testerStore'
import { Code, Languages, Send, RefreshCcw } from 'lucide-vue-next'

const store = useTesterStore()

const emit = defineEmits(['generate'])

const handleGenerate = () => {
  emit('generate')
}
</script>

<template>
  <section class="flex flex-col space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-semibold text-gray-300 flex items-center space-x-2">
        <Languages class="w-4 h-4 text-blue-500" />
        <span>Source Code</span>
      </h2>
    </div>
    
    <div class="flex-1 relative group">
      <textarea
        v-model="store.inputCode"
        placeholder="Paste your source code here..."
        class="w-full h-full bg-gray-900 border border-gray-800 p-6 rounded-2xl outline-none focus:border-blue-500/50 transition-colors text-sm font-mono text-gray-300 resize-none custom-scrollbar"
      ></textarea>
      
      <button 
        @click="handleGenerate"
        :disabled="store.isGenerating || !store.inputCode.trim()"
        class="absolute bottom-6 right-6 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-xl shadow-2xl shadow-blue-900/20 transition-all flex items-center space-x-2 group-focus-within:scale-105 active:scale-95"
      >
        <Send v-if="!store.isGenerating" class="w-4 h-4" />
        <RefreshCcw v-else class="w-4 h-4 animate-spin" />
        <span class="font-semibold">{{ store.isGenerating ? 'Thinking...' : (store.isLoggedIn ? 'Generate' : 'Login to Start') }}</span>
      </button>
      
      <div v-if="!store.isLoggedIn" class="absolute inset-0 bg-gray-950/40 backdrop-blur-[2px] rounded-2xl flex items-center justify-center">
        <p class="text-xs font-medium text-white bg-blue-600 px-4 py-2 rounded-full shadow-xl">Please Login First</p>
      </div>
      
      <p class="absolute -bottom-6 right-2 text-[9px] text-gray-600 font-medium">
        Rate Limit: 5 requests / min per IP
      </p>
    </div>
  </section>
</template>
