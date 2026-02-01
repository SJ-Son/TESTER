import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as generatorApi from '../api/generator'

export const useTesterStore = defineStore('tester', () => {
    // State
    const inputCode = ref('')
    const generatedCode = ref('')
    const selectedLanguage = ref('python')
    const selectedModel = ref('gemini-3-flash-preview')
    const isGenerating = ref(false)
    const error = ref<string | null>(null)
    const streamEnded = ref(false)
    const userToken = ref(localStorage.getItem('tester_token') || '')
    const history = ref<any[]>([])

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

    const loadHistory = () => {
        const savedHistory = localStorage.getItem('tester_history')
        if (savedHistory) {
            try {
                history.value = JSON.parse(savedHistory)
            } catch (e) {
                console.error('Failed to parse history', e)
                history.value = []
            }
        }
    }

    const addToHistory = (input: string, result: string, language: string) => {
        if (!result || result.startsWith('ERROR:')) return

        if (history.value.length > 0) {
            const lastItem = history.value[0]
            if (lastItem.inputCode === input && lastItem.result === result) {
                return
            }
        }

        const newItem = {
            id: Date.now(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            inputCode: input,
            result: result,
            language: language
        }

        history.value.unshift(newItem)

        if (history.value.length > 5) {
            history.value = history.value.slice(0, 5)
        }

        localStorage.setItem('tester_history', JSON.stringify(history.value))
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
        isLoggedIn,
        setToken,
        clearToken,
        loadHistory,
        addToHistory,
        restoreHistory,
        generateTestCode
    }
})
