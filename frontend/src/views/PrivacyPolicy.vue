<script setup lang="ts">
/**
 * 개인정보처리방침 표시 페이지.
 */
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
// @ts-ignore
import privacyRaw from '../../../docs/privacy_policy.md?raw'

const renderedContent = computed(() => {
  const rawHtml = marked(privacyRaw)
  return DOMPurify.sanitize(rawHtml as string)
})
</script>

<template>
  <div class="h-full overflow-y-auto px-4 py-8 custom-scrollbar">
    <div class="max-w-3xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl relative">
      <h1 class="text-3xl font-bold text-white mb-6 border-b border-gray-800 pb-4">개인정보처리방침</h1>
      
      <!-- Rendered Markdown/HTML -->
      <div class="text-sm text-gray-400 leading-relaxed" v-html="renderedContent"></div>

      <div class="mt-10 pt-6 border-t border-gray-800 flex justify-center">
        <router-link to="/" class="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium text-sm">
          홈으로 돌아가기
        </router-link>
      </div>
    </div>
  </div>
</template>
