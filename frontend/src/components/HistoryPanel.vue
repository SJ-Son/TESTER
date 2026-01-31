<script setup lang="ts">
import { useTesterStore } from '../stores/testerStore'
import { History, Clock, Code2, ChevronRight } from 'lucide-vue-next'

const store = useTesterStore()

const handleRestore = (item: any) => {
  store.restoreHistory(item)
}
</script>

<template>
  <div class="space-y-4">
    <label class="text-xs font-semibold text-gray-500 uppercase tracking-widest flex items-center space-x-2">
      <History class="w-3 h-3" />
      <span>Recent History</span>
    </label>

    <div v-if="store.history.length === 0" class="p-4 rounded-xl border border-gray-800 bg-gray-900/50 text-center">
      <p class="text-[10px] text-gray-500 font-medium italic">No history yet</p>
    </div>

    <div v-else class="space-y-2">
      <button 
        v-for="item in store.history" 
        :key="item.id"
        @click="handleRestore(item)"
        class="w-full text-left p-3 rounded-xl border border-gray-800 bg-gray-900 hover:bg-gray-800 hover:border-gray-700 transition-all group relative overflow-hidden"
      >
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center space-x-2">
            <Clock class="w-3 h-3 text-blue-400/70" />
            <span class="text-[10px] font-mono text-gray-400">{{ item.timestamp }}</span>
          </div>
          <div class="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
            <Code2 class="w-2.5 h-2.5 text-blue-400" />
            <span class="text-[9px] font-bold text-blue-400 uppercase tracking-tight">{{ item.language }}</span>
          </div>
        </div>
        <div class="text-[11px] text-gray-300 line-clamp-1 font-mono opacity-60">
          {{ item.inputCode.trim().substring(0, 50) }}...
        </div>
        
        <div class="absolute right-2 bottom-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <ChevronRight class="w-3 h-3 text-blue-400" />
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
