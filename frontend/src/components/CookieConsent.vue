<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isVisible = ref(false)

// Declare gtag in the window object to avoid TS errors
declare global {
  interface Window {
    gtag: (...args: any[]) => void
  }
}

onMounted(() => {
  const storedConsent = localStorage.getItem('cookie_consent')

  if (!storedConsent) {
    // No consent choice made yet, show banner
    // Delay slightly for better UX (don't pop up instantly on load)
    setTimeout(() => {
      isVisible.value = true
    }, 1000)
  } else if (storedConsent === 'granted') {
    // User previously granted consent, update gtag
    updateConsent('granted')
  }
  // If denied, we do nothing as the default is already 'denied'
})

const updateConsent = (status: 'granted' | 'denied') => {
  if (window.gtag) {
    window.gtag('consent', 'update', {
      'ad_storage': status,
      'ad_user_data': status,
      'ad_personalization': status,
      'analytics_storage': status
    })
  }
}

const acceptCookies = () => {
  localStorage.setItem('cookie_consent', 'granted')
  updateConsent('granted')
  isVisible.value = false
}

const rejectCookies = () => {
  localStorage.setItem('cookie_consent', 'denied')
  updateConsent('denied')
  isVisible.value = false
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-500 ease-out"
    enter-from-class="opacity-0 translate-y-8"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-300 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-8"
  >
    <div
      v-if="isVisible"
      class="fixed bottom-4 left-4 right-4 md:left-auto md:right-8 z-[100] max-w-sm"
    >
      <div 
        class="bg-gray-900/95 backdrop-blur-md border border-gray-800 rounded-xl shadow-2xl p-6 ring-1 ring-white/10"
      >
        <div class="flex flex-col gap-4">
          <!-- Icon & Text -->
          <div class="flex items-start gap-3">
            <div class="p-2 bg-emerald-500/10 rounded-lg shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-white">쿠키 사용 및 개인정보 보호</h3>
              <p class="text-xs text-gray-400 mt-1 leading-relaxed">
                서비스 품질 향상과 사용자 분석을 위해 쿠키를 사용합니다.<br>
                귀하의 정보는 안전하게 관리됩니다.
              </p>
            </div>
          </div>

          <!-- Buttons -->
          <div class="flex gap-2.5 pt-1">
            <button
              @click="rejectCookies"
              class="flex-1 px-4 py-2 text-xs font-medium text-gray-400 hover:text-white bg-transparent hover:bg-white/5 rounded-lg transition-colors"
            >
              필수 항목만
            </button>
            <button
              @click="acceptCookies"
              class="flex-1 px-4 py-2 text-xs font-medium text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-lg shadow-emerald-900/20 transition-all transform hover:scale-[1.02]"
            >
              모두 동의
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
