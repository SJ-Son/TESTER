import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
    // State
    const userToken = ref(localStorage.getItem('tester_token') || '')
    const isLoggedIn = computed(() => !!userToken.value)

    // Actions
    const setToken = (token: string) => {
        userToken.value = token
        localStorage.setItem('tester_token', token)
    }

    const clearToken = () => {
        userToken.value = ''
        localStorage.removeItem('tester_token')
    }

    const initializeAuth = () => {
        import('../api/supabase').then(({ supabase }) => {
            supabase.auth.onAuthStateChange((event, session) => {
                if (session?.access_token) {
                    setToken(session.access_token)
                    // Clean up URL hash if it contains auth tokens
                    if (window.location.hash && window.location.hash.includes('access_token')) {
                        window.history.replaceState(null, '', window.location.pathname + window.location.search)
                    }
                } else if (event === 'SIGNED_OUT') {
                    // Prevent clearing token in E2E tests where we mock auth
                    if (localStorage.getItem('E2E_TEST_MODE') === 'true') {
                        return
                    }
                    clearToken()
                }
            })
        })
    }

    const loginWithGoogle = async () => {
        const { supabase } = await import('../api/supabase')
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) {
            console.error('Login failed:', error)
            throw error
        }
    }

    const logout = async () => {
        const { supabase } = await import('../api/supabase')
        await supabase.auth.signOut()
        clearToken()
    }

    // Auto-initialize on store creation
    initializeAuth()

    return {
        userToken,
        isLoggedIn,
        loginWithGoogle,
        logout
    }
})
