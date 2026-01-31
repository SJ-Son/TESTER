import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
        // Validation: Ensure result is not empty and not an error
        if (!result || result.startsWith('ERROR:')) return

        // Duplicate Prevention: Check if identical to the most recent item
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

        // Limit to 5 items
        if (history.value.length > 5) {
            history.value = history.value.slice(0, 5)
        }

        localStorage.setItem('tester_history', JSON.stringify(history.value))
    }

    const restoreHistory = (item: any) => {
        inputCode.value = item.inputCode
        generatedCode.value = item.result
        selectedLanguage.value = item.language
        // Set streamEnded to true since we are restoring a completed result
        streamEnded.value = true
    }

    const generateTestCode = async (recaptchaToken: string) => {
        if (!inputCode.value.trim() || !isLoggedIn.value) return

        error.value = ''
        generatedCode.value = ''
        isGenerating.value = true
        // Safeguard: Reset streamEnded immediately
        streamEnded.value = false

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken.value}`
                },
                body: JSON.stringify({
                    input_code: inputCode.value,
                    language: selectedLanguage.value,
                    model: selectedModel.value,
                    recaptcha_token: recaptchaToken
                })
            })

            if (!response.ok) throw new Error('Failed to connect to server')

            const reader = response.body?.getReader()
            if (!reader) throw new Error('No stream available')

            const decoder = new TextDecoder()

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, { stream: true })

                if (chunk.startsWith('ERROR:')) {
                    error.value = chunk.replace('ERROR:', '').trim()
                    break
                }

                generatedCode.value += chunk
            }
        } catch (err: any) {
            error.value = err.message
        } finally {
            isGenerating.value = false
            streamEnded.value = true

            // Refinement: Add to history directly here when successfully completed
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
