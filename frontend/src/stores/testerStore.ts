import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import * as generatorApi from '../api/generator'
import { MOBILE_BREAKPOINT, MAX_HISTORY_ITEMS } from '../utils/constants'
import type { SupportedLanguage, GeminiModel } from '../types'

export const useTesterStore = defineStore('tester', () => {
    // State
    /** The source code input by the user */
    const inputCode = ref('')
    /** The generated test code from the API */
    const generatedCode = ref('')
    /** The programming language selected */
    const selectedLanguage = ref<SupportedLanguage>('python')
    /** The selected Gemini model */
    const selectedModel = ref<GeminiModel>('gemini-3-flash-preview')
    /** Whether code generation is in progress */
    const isGenerating = ref(false)
    /** Error message if any operation fails */
    const error = ref<string | null>(null)
    /** Whether the streaming response has ended */
    const streamEnded = ref(false)
    /** The user's authentication token */
    const userToken = ref(localStorage.getItem('tester_token') || '')
    /** User's weekly usage statistics */
    const usageStats = ref({ weekly_usage: 0, weekly_limit: 30, remaining: 30 })

    // Initialize history from local storage safely
    let initialHistory: any[] = []
    try {
        const stored = localStorage.getItem('tester_history')
        if (stored) {
            initialHistory = JSON.parse(stored)
        }
    } catch (e) {
        console.error('Failed to parse history from local storage', e)
    }
    const history = ref<any[]>(initialHistory)

    const isSidebarOpen = ref(false)
    const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)

    // Watchers for Offline-First Storage
    watch(history, (newHistory) => {
        localStorage.setItem('tester_history', JSON.stringify(newHistory))
    }, { deep: true })

    // Computed
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

    // Initialize Auth Listener
    // This should be called once, typically in App.vue or main.ts, but initializing store logic here works too.
    // However, store setup function runs once.
    import('../api/supabase').then(({ supabase }) => {
        supabase.auth.onAuthStateChange((event, session) => {
            if (session?.access_token) {
                setToken(session.access_token)
                fetchUserStatus() // Fetch status on login
                // Clean up URL hash if it contains auth tokens
                if (window.location.hash && window.location.hash.includes('access_token')) {
                    window.history.replaceState(null, '', window.location.pathname + window.location.search)
                }
            } else if (event === 'SIGNED_OUT') {
                clearToken()
            }
        })
    })

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

    const fetchUserStatus = async () => {
        if (!isLoggedIn.value) return

        try {
            const { supabase } = await import('../api/supabase')
            // Using direct fetch wrapper for custom endpoint if available, but here we can just fetch
            // Or ideally use the generatorApi or a new userApi. Let's stick to fetch for now as it's simple.
            const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/user/status`, {
                // Wait, the backend is not a supabase function, it's our FastAPI backend.
                // We need to use the same base URL logic as generatorApi.
                // Let's assume relative path /api/user/status connects to our FastAPI backend proxy or direct.
                // Since we are in the same domain (or proxy), let's use /api/user/status
            })

            // Correct approach: Use the authenticated fetch
            const res = await fetch('/api/user/status', {
                headers: {
                    'Authorization': `Bearer ${userToken.value}`
                }
            })

            if (res.ok) {
                const data = await res.json()
                usageStats.value = {
                    weekly_usage: data.weekly_usage,
                    weekly_limit: data.weekly_limit,
                    remaining: data.remaining
                }
            }
        } catch (e) {
            console.error('Failed to fetch user status', e)
        }
    }

    const loadHistory = async () => {
        if (!isLoggedIn.value) return

        try {
            const historyData = await generatorApi.fetchHistory(userToken.value)
            if (Array.isArray(historyData)) {
                // Ensure we merge or replace cautiously. Here we replace for simplicity as per requirement.
                history.value = historyData.map((item: any) => ({
                    id: item.id,
                    input_code: item.input_code,
                    generated_code: item.generated_code,
                    language: item.language,
                    created_at: item.created_at,
                    // View helpers
                    timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    inputCode: item.input_code, // Maintain compatibility with view
                    result: item.generated_code // Maintain compatibility with view
                }))
            }
        } catch (e) {
            console.error('Failed to load history from server, keeping local cache:', e)
            // Do not clear history.value
        }
    }

    const addToHistory = (input: string, result: string, language: SupportedLanguage) => {
        // Matches backend schema
        const now = new Date().toISOString()
        const newItem = {
            id: 'temp-' + Date.now(),
            input_code: input,
            generated_code: result,
            language: language,
            created_at: now,
            // View helpers
            timestamp: new Date(now).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            inputCode: input,
            result: result
        }
        history.value.unshift(newItem)
        if (history.value.length > MAX_HISTORY_ITEMS) {
            history.value.pop()
        }
    }

    const executeTest = async () => {
        if (!generatedCode.value || !isLoggedIn.value) return null

        try {
            return await generatorApi.executeTestCode(inputCode.value, generatedCode.value, selectedLanguage.value, userToken.value)
        } catch (e: any) {
            return { success: false, error: e.message, output: '' }
        }
    }

    const restoreHistory = (item: any) => {
        inputCode.value = item.inputCode
        generatedCode.value = item.result
        selectedLanguage.value = item.language
        streamEnded.value = true
    }

    /**
     * Generates test code using the Gemini API.
     * Handles streaming responses and updates the state in real-time.
     *
     * @param turnstileToken - The Cloudflare Turnstile token for verification.
     */
    const generateTestCode = async (turnstileToken: string) => {
        if (!inputCode.value.trim() || !isLoggedIn.value) return

        error.value = ''
        generatedCode.value = ''
        isGenerating.value = true
        streamEnded.value = false

        try {
            await generatorApi.generateTestCode(
                {
                    input_code: inputCode.value,
                    language: selectedLanguage.value,
                    model: selectedModel.value,
                    turnstile_token: turnstileToken
                },
                userToken.value,
                (chunk: string) => {
                    generatedCode.value += chunk
                },
                (errorMsg: string) => {
                    error.value = errorMsg
                }
            )
        } catch (err: any) {
            error.value = err.message
        } finally {
            isGenerating.value = false
            streamEnded.value = true

            if (generatedCode.value && !error.value) {
                addToHistory(inputCode.value, generatedCode.value, selectedLanguage.value)
                fetchUserStatus() // Update quota after generation
            }
        }
    }

    return {
        inputCode,
        generatedCode,
        selectedLanguage,
        selectedModel,
        isGenerating,
        error,
        streamEnded,
        userToken,
        history,
        isSidebarOpen,
        isMobile,
        isLoggedIn,
        loginWithGoogle,
        logout,
        loadHistory,
        addToHistory,
        restoreHistory,
        generateTestCode,
        executeTest,
        usageStats,
        fetchUserStatus
    }
})
