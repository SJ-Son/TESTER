import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth'
import * as generatorApi from '../api/generator'
import { MAX_HISTORY_ITEMS } from '../utils/constants'
import type { SupportedLanguage } from '../types'

export const useHistoryStore = defineStore('history', () => {
    const authStore = useAuthStore()
    const history = ref<any[]>([])

    // Sync with local storage for offline support
    watch(history, (newHistory) => {
        localStorage.setItem('tester_history', JSON.stringify(newHistory))
    }, { deep: true })

    // Automatically load history when user logs in (fixes refresh issue)
    watch(() => authStore.isLoggedIn, (isLoggedIn) => {
        if (isLoggedIn) {
            loadHistory()
        } else {
            history.value = [] // Clear history on logout
        }
    }, { immediate: true })

    const loadHistory = async () => {
        if (!authStore.isLoggedIn) return

        try {
            const historyData = await generatorApi.fetchHistory(authStore.userToken)
            if (Array.isArray(historyData)) {
                history.value = historyData.map((item: any) => ({
                    id: item.id,
                    timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    inputCode: item.input_code,
                    result: item.generated_code,
                    language: item.language
                }))
            }
        } catch (e) {
            console.error('Failed to load history:', e)
            // Note: In offline mode, this is expected behavior
        }
    }

    const addToHistory = (input: string, result: string, language: SupportedLanguage) => {
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
    }

    return {
        history,
        loadHistory,
        addToHistory
    }
})
