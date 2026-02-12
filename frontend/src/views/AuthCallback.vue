<script setup lang="ts">
/**
 * OAuth 인증 콜백 페이지.
 * Supabase 인증 후 세션을 확인하고 홈으로 리디렉션합니다.
 */
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { supabase } from '../api/supabase'
import { useTesterStore } from '../stores/testerStore'

const router = useRouter()
const route = useRoute()
const store = useTesterStore()

onMounted(async () => {
  // URL에서 에러 확인 (예: ?error=access_denied&error_description=...)
  const errorDescription = route.query.error_description as string
  const error = route.query.error as string

  if (error || errorDescription) {
    console.error('인증 콜백 에러:', error, errorDescription)
    store.error = errorDescription || error || '인증에 실패했습니다'
    router.replace('/')
    return
  }

  const { data } = await supabase.auth.getSession()
  
  if (data.session) {
    // 세션이 유효하면 즉시 홈으로 이동
    router.replace('/')
  } else {
    // 세션이 아직 없으면 인증 상태 변경 이벤트를 대기 (코드가 처리 중일 수 있음)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        router.replace('/')
      }
      // 에러 이벤트나 로그아웃 발생 시 홈으로 리디렉션
      if (event === 'SIGNED_OUT') {
         // 교환 실패 시 여기로 올 수 있음.
         // 다시 시도하거나 로그아웃 상태를 보여주기 위해 홈으로 이동.
         router.replace('/')
      }
    })

    // 안전장치: 아무 일도 일어나지 않을 경우(유효하지 않은 코드 등)를 대비한 타임아웃
    setTimeout(() => {
        router.replace('/')
    }, 5000)
  }
})
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-950 text-gray-200">
    <div class="flex flex-col items-center space-y-4">
      <!-- Simple Loading Spinner -->
      <div class="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      <p class="text-sm font-mono text-gray-400 animate-pulse">Authenticating...</p>
    </div>
  </div>
</template>
