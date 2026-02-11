<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTesterStore } from '../stores/testerStore'

const router = useRouter()
const store = useTesterStore()

onMounted(() => {
  // The token parsing is handled by the supabase client in the store's init logic.
  // We just need to give it a moment to process the hash, then redirect to home.
  // Ideally, we could check if session is established here.
  
  // Wait for a brief moment to allow the onAuthStateChange in store to fire
  // or we can manually check session using store logic if needed.
  // But since the hash containing the token is on this URL, 
  // Supabase's onAuthStateChange (initialized in store) will catch it.
  
  // Let's set a small timeout or watch for isLoggedIn
  const checkAuth = setInterval(() => {
    if (store.isLoggedIn) {
      clearInterval(checkAuth)
      router.replace('/')
    }
  }, 100)

  // Fallback in case something goes wrong or it was just a revisit
  setTimeout(() => {
    clearInterval(checkAuth)
    router.replace('/')
  }, 3000)
})
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-900 text-white">
    <div class="flex flex-col items-center space-y-4">
      <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm text-gray-400">Authenticating...</p>
    </div>
  </div>
</template>
