import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import * as generatorApi from '../api/generator'
import { MOBILE_BREAKPOINT, MAX_HISTORY_ITEMS } from '../utils/constants'
import type { SupportedLanguage, GeminiModel } from '../types'
import type { TokenInfo } from '../types/api.types'

export const useTesterStore = defineStore('tester', () => {
    // State
    /** 사용자가 입력한 소스 코드 */
    const inputCode = ref('')
    /** API로부터 생성된 테스트 코드 */
    const generatedCode = ref('')
    /** 선택된 프로그래밍 언어 */
    const selectedLanguage = ref<SupportedLanguage>('python')
    /** 선택된 Gemini 모델 */
    const selectedModel = ref<GeminiModel>('gemini-3-flash-preview')
    /** 코드 생성 진행 중 여부 */
    const isGenerating = ref(false)
    /** 작업 실패 시 에러 메시지 */
    const error = ref<string | null>(null)
    /** 스트리밍 응답 종료 여부 */
    const streamEnded = ref(false)
    /** 사용자의 인증 토큰 */
    const userToken = ref(localStorage.getItem('tester_token') || '')
    /** 사용자의 주간 사용량 통계 */
    /** 사용자의 토큰 정보 */
    const tokenInfo = ref<TokenInfo>({
        current_tokens: 0,
        daily_bonus_claimed: false,
        cost_per_generation: 10,
        daily_ad_remaining: 10
    })
    /** 토큰 부족 모달 표시 여부 */
    const showInsufficientTokensModal = ref(false)

    /** @deprecated 하위 호환성 유지 — tokenInfo 사용 권장 */
    const usageStats = computed(() => ({
        weekly_usage: 0,
        weekly_limit: 30,
        remaining: tokenInfo.value.cost_per_generation > 0
            ? Math.floor(tokenInfo.value.current_tokens / tokenInfo.value.cost_per_generation)
            : 0
    }))

    // 로컬 스토리지에서 히스토리 초기화 (안전하게 파싱)
    let initialHistory: any[] = []
    try {
        const stored = localStorage.getItem('tester_history')
        if (stored) {
            initialHistory = JSON.parse(stored)
        }
    } catch (e) {
        console.error('로컬 스토리지에서 히스토리 파싱 실패', e)
    }
    const history = ref<any[]>(initialHistory)

    const isSidebarOpen = ref(false)
    const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)

    // 오프라인 우선(Offline-First) 스토리지를 위한 Watcher
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

    // 인증 리스너 초기화
    // 일반적으로 App.vue나 main.ts에서 호출되어야 하지만, 스토어 로직을 여기에 두는 것도 동작함.
    import('../api/supabase').then(({ supabase }) => {
        supabase.auth.onAuthStateChange((event, session) => {
            if (session?.access_token) {
                setToken(session.access_token)
                fetchUserStatus() // 로그인 시 상태 조회
                // URL 해시에 인증 토큰이 포함된 경우 정리
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
                redirectTo: `${window.location.origin}/auth/callback`,
                // @ts-ignore: flowType은 런타임에 유효하지만 타입 정의가 구버전일 수 있음
                flowType: 'pkce'
            }
        })
        if (error) {
            console.error('로그인 실패:', error)
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
            const res = await fetch('/api/user/status', {
                headers: {
                    'Authorization': `Bearer ${userToken.value}`
                }
            })

            if (res.ok) {
                const data = await res.json()
                if (data.token_info) {
                    tokenInfo.value = data.token_info
                }
            }
        } catch (e) {
            console.error('사용자 상태 조회 실패', e)
        }
    }

    const loadHistory = async () => {
        if (!isLoggedIn.value) return

        try {
            const historyData = await generatorApi.fetchHistory(userToken.value)
            if (Array.isArray(historyData)) {
                // 병합 대신 단순 교체 (요구사항 단순화)
                history.value = historyData.map((item: any) => ({
                    id: item.id,
                    input_code: item.input_code,
                    generated_code: item.generated_code,
                    language: item.language,
                    created_at: item.created_at,
                    // 뷰 헬퍼 속성
                    timestamp: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    inputCode: item.input_code, // 뷰 호환성 유지
                    result: item.generated_code // 뷰 호환성 유지
                }))
            }
        } catch (e) {
            console.error('서버에서 히스토리 로드 실패, 로컬 캐시 유지:', e)
            // history.value를 초기화하지 않음 (오프라인 데이터 보존)
        }
    }

    const addToHistory = (input: string, result: string, language: SupportedLanguage) => {
        // 백엔드 스키마와 일치
        const now = new Date().toISOString()
        const newItem = {
            id: 'temp-' + Date.now(),
            input_code: input,
            generated_code: result,
            language: language,
            created_at: now,
            // 뷰 헬퍼 속성
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
     * Gemini API를 사용하여 테스트 코드를 생성합니다.
     * 스트리밍 응답을 처리하고 상태를 실시간으로 업데이트합니다.
     *
     * @param turnstileToken - 검증을 위한 Cloudflare Turnstile 토큰.
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
                    // 토큰 부족 에러 시 모달 표시
                    if (errorMsg.includes('INSUFFICIENT_TOKENS') || errorMsg.includes('토큰이 부족')) {
                        showInsufficientTokensModal.value = true
                    }
                    error.value = errorMsg
                }
            )
        } catch (err: any) {
            if (err.message?.includes('INSUFFICIENT_TOKENS')) {
                showInsufficientTokensModal.value = true
            }
            error.value = err.message
        } finally {
            isGenerating.value = false
            streamEnded.value = true

            if (generatedCode.value && !error.value) {
                addToHistory(inputCode.value, generatedCode.value, selectedLanguage.value)
                fetchUserStatus() // 생성 후 토큰 정보 업데이트
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
        tokenInfo,
        showInsufficientTokensModal,
        usageStats,
        fetchUserStatus
    }
})
