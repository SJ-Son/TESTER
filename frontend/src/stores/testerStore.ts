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
    /** The current user profile */
    const user = ref<any>(null)
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
    const isLoggedIn = computed(() => !!user.value)

    // Actions
    const loginWithGoogle = async () => {
        // Redirect to Backend Login Endpoint
        window.location.href = '/api/auth/login?provider=google'
    }

    const logout = async () => {
        try {
            await fetch('/api/auth/logout', { method: 'POST' })
            user.value = null
            window.location.href = '/'
        } catch (error) {
            console.error('Logout failed', error)
        }
    }

    const fetchUserStatus = async () => {
        try {
            const res = await fetch('/api/user/status')
            if (res.ok) {
                const data = await res.json()
                // Update User State
                user.value = { email: data.email }

                usageStats.value = {
                    weekly_usage: data.weekly_usage,
                    weekly_limit: data.weekly_limit,
                    remaining: data.remaining
                }
            } else if (res.status === 401) {
                user.value = null
            }
        } catch (e) {
            console.error('Failed to fetch user status', e)
            user.value = null
        }
    }

    const loadHistory = async () => {
        if (!isLoggedIn.value) return

        try {
            // No token needed, cookie is sent automatically
            const historyData = await generatorApi.fetchHistory()
            if (Array.isArray(historyData)) {
                history.value = historyData.map((item: any) => ({
                    id: item.id,
                    input_code: item.input_code,
                    generated_code: item.generated_code,
                    language: item.language,
                    created_at: item.created_at,
                    timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    inputCode: item.input_code,
                    result: item.generated_code
                }))
            }
        } catch (e) {
            console.error('Failed to load history from server, keeping local cache:', e)
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
            return await generatorApi.executeTestCode(inputCode.value, generatedCode.value, selectedLanguage.value)
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

    // Initialize: Check if user is logged in via cookie
    fetchUserStatus()

    return {
        inputCode,
        generatedCode,
        selectedLanguage,
        selectedModel,
        isGenerating,
        error,
        streamEnded,
        user,
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
