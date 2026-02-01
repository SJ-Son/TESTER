<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
// @ts-ignore
import changelogRaw from '../../../CHANGELOG.md?raw'

const renderedMarkdown = computed(() => {
  return marked(changelogRaw)
})
</script>

<template>
  <div class="h-full overflow-y-auto px-4 py-8 custom-scrollbar">
    <div class="max-w-3xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl relative">
      <!-- Custom Header -->
      <div class="flex items-center justify-between border-b border-gray-800 pb-4 mb-6">
        <h1 class="text-3xl font-bold text-white">
          <span class="text-blue-500">Change</span>log
        </h1>
        <div class="text-xs text-gray-500 font-mono">
          Synced with CHANGELOG.md
        </div>
      </div>
      
      <!-- Markdown Content -->
      <div class="prose prose-invert prose-sm max-w-none 
                  prose-headings:text-gray-100 prose-headings:font-bold prose-headings:mb-2 prose-headings:mt-6
                  prose-p:text-gray-400 prose-p:leading-relaxed prose-p:my-2
                  prose-ul:my-2 prose-li:my-0.5
                  prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-white prose-strong:font-semibold
                  prose-code:text-blue-300 prose-code:bg-gray-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-[''] prose-code:after:content-['']"
           v-html="renderedMarkdown">
      </div>

      <!-- Navigation -->
      <div class="mt-10 pt-6 border-t border-gray-800 flex justify-center">
        <router-link to="/" class="px-6 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors font-medium text-sm">
          돌아가기
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom tweaks if Tailwind prose isn't usually sufficient */
:deep(h1) {
  display: none; /* Hide the duplicated "Changelog" title from md */
}
:deep(h2) {
  font-size: 1.25rem;
  border-bottom: 1px solid #374151;
  padding-bottom: 0.5rem;
  margin-top: 2rem;
  color: #60a5fa; /* blue-400 */
}
:deep(h3) {
  font-size: 1rem;
  margin-top: 1.5rem;
  color: #e5e7eb;
}
:deep(ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
}
</style>
