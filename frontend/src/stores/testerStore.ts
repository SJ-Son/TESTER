import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as generatorApi from '../api/generator'
import { MOBILE_BREAKPOINT, MAX_HISTORY_ITEMS } from '../utils/constants'
import type { SupportedLanguage, GeminiModel } from '../types'

export const useTesterStore = defineStore('tester', () => {
    // State
    const inputCode = ref('')
    const generatedCode = ref('')
    const selectedLanguage = ref<SupportedLanguage>('python')
    const selectedModel = ref<GeminiModel>('gemini-3-flash-preview')
    const isGenerating = ref(false)
    const error = ref<string | null>(null)
    const streamEnded = ref(false)
    const userToken = ref(localStorage.getItem('tester_token') || '')
    const history = ref<any[]>([])

    const isSidebarOpen = ref(false)
    const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)

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

    const loadHistory = async () => {
        if (!isLoggedIn.value) return

        try {
            const historyData = await generatorApi.fetchHistory(userToken.value)
            history.value = historyData.map((item: any) => ({
                id: item.id,
                timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                inputCode: item.input_code,
                result: item.generated_code,
                language: item.language
            }))
        } catch (e) {
            console.error('Failed to load history', e)
        }
    }

    const addToHistory = (input: string, result: string, language: SupportedLanguage) => {
        // Optimistic update or just reload. 
        // For better UX, we can just push to local list, but ID will be missing.
        // We will reload history when sidebar is opened or just push a temporary item.
        // For now, let's just reload history silently if possible, or append simple item.
        const newItem = {
            id: 'temp-' + Date.now(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            inputCode: input,
            result: result,
            language: language
        }
        history.value.unshift(newItem)
        if (history.value.length > MAX_HISTORY_ITEMS) {
            history.value.pop()
        }
        // In background, we could fetch fresh history.
    }

    const executeTest = async () => {
        if (!generatedCode.value || !isLoggedIn.value) return null

        try {
            return await generatorApi.executeTestCode(generatedCode.value, selectedLanguage.value, userToken.value)
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
        setToken,
        clearToken,
        loadHistory,
        addToHistory,
        restoreHistory,
        generateTestCode,
        executeTest
    }
})
