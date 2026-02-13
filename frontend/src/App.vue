<script setup lang="ts">
/**
 * 최상위 루트 컴포넌트.
 * 전역 레이아웃, 모달 처리, 쿠키 동의 배너를 관리합니다.
 */
import { RouterView, useRoute, useRouter } from 'vue-router'
import HomeView from './views/HomeView.vue'
import CookieConsent from './components/CookieConsent.vue'

const route = useRoute()
const router = useRouter()

/**
 * 모달 배경 클릭 시 홈으로 이동하여 모달을 닫습니다.
 * @param e 마우스 이벤트
 */
const closeModal = (e: MouseEvent) => {
  // 배경(backdrop)을 클릭한 경우에만 닫기 (내부 컨텐츠 클릭 제외)
  if (e.target === e.currentTarget) {
    router.push('/')
  }
}
</script>

<template>
  <div class="relative w-full h-full min-h-screen overflow-hidden">
    <!-- Background Layer: Always render HomeView -->
    <HomeView class="absolute inset-0 z-0" />

    <!-- Overlay Layer: Renders Privacy, Terms, Changelog -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="route.path !== '/'" 
        class="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 md:p-8"
        @click="closeModal"
      >
        <div class="w-full max-w-4xl max-h-full overflow-hidden flex flex-col relative" @click.stop>
           <!-- Close Button (Mobile/Desktop convenience) -->
           <button 
             @click="router.push('/')"
             class="absolute top-4 right-4 z-50 p-2 bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white rounded-full transition-colors backdrop-blur-md"
           >
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
               <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
             </svg>
           </button>
           
           <!-- Content -->
           <RouterView v-slot="{ Component }">
             <Transition
               enter-active-class="transition duration-300 ease-out delay-100"
               enter-from-class="opacity-0 translate-y-4 scale-95"
               enter-to-class="opacity-100 translate-y-0 scale-100"
               leave-active-class="transition duration-200 ease-in"
               leave-from-class="opacity-100 translate-y-0 scale-100"
               leave-to-class="opacity-0 translate-y-4 scale-95"
             >
               <component :is="Component" />
             </Transition>
           </RouterView>
        </div>
      </div>

    </Transition>
    <!-- Global Cookie Consent Banner -->
    <CookieConsent />
  </div>
</template>

<style>
/* Global styles to match main branch */
:root {
  color-scheme: dark;
}

html, body {
  background-color: #030712; /* bg-gray-950 */
  color-scheme: dark;
}

/* Custom Scrollbar for all */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.1);
}

pre {
  background: transparent !important;
  padding: 0 !important;
}
code {
  background: transparent !important;
}
</style>
