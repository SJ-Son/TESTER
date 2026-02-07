import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as generatorApi from '../api/generator'
import { MOBILE_BREAKPOINT } from '../utils/constants'
import type { SupportedLanguage, GeminiModel } from '../types'
import { useAuthStore } from './auth'
import { useHistoryStore } from './history'

export const useGeneratorStore = defineStore('generator', () => {
    // State
    const inputCode = ref('')
    const generatedCode = ref('')
    const selectedLanguage = ref<SupportedLanguage>('python')
    const selectedModel = ref<GeminiModel>('gemini-3-flash-preview')
    const isGenerating = ref(false)
    const error = ref<string | null>(null)
    const streamEnded = ref(false)

    // UI State (kept here for convenience as it relates to the generator layout)
    const isSidebarOpen = ref(false)
    const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)

    const authStore = useAuthStore()
    const historyStore = useHistoryStore()

    const executeTest = async () => {
        if (!generatedCode.value || !authStore.isLoggedIn) return null

        try {
            return await generatorApi.executeTestCode(
                inputCode.value,
                generatedCode.value,
                selectedLanguage.value,
                authStore.userToken
            )
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
        if (!inputCode.value.trim() || !authStore.isLoggedIn) return

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
                authStore.userToken,
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
                historyStore.addToHistory(inputCode.value, generatedCode.value, selectedLanguage.value)
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
        isSidebarOpen,
        isMobile,
        generateTestCode,
        executeTest,
        restoreHistory
    }
})
