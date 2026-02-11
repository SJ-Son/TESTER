<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { supabase } from '../api/supabase'
import { useTesterStore } from '../stores/testerStore'

const router = useRouter()
const route = useRoute()
const store = useTesterStore()

onMounted(async () => {
  // Check for errors in the URL (e.g., ?error=access_denied&error_description=...)
  const errorDescription = route.query.error_description as string
  const error = route.query.error as string

  if (error || errorDescription) {
    console.error('Auth Callback Error:', error, errorDescription)
    store.error = errorDescription || error || 'Authentication failed'
    router.replace('/')
    return
  }

  const { data } = await supabase.auth.getSession()
  
  if (data.session) {
    // Session is valid, replace with home immediately
    router.replace('/')
  } else {
    // If no session yet, wait for the auth state change event which might be processing the code
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        router.replace('/')
      }
      // If we get an error event or signed out, we might want to go home too, 
      // maybe with an error query param if needed, but for now just redirect.
      if (event === 'SIGNED_OUT') {
         // If exchange failed, we might end up here. 
         // Let's redirect to home to try again or show logged out state.
         router.replace('/')
      }
    })

    // Safety timeout: in case nothing happens (e.g. invalid code), don't get stuck forever.
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
