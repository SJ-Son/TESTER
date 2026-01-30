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

    const generateTestCode = async (recaptchaToken: string) => {
        if (!inputCode.value.trim() || !isLoggedIn.value) return

        error.value = ''
        generatedCode.value = ''
        isGenerating.value = true
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
        isLoggedIn,
        setToken,
        clearToken,
        generateTestCode
    }
})
