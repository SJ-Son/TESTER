<script setup lang="ts">
/**
 * 광고 시청 보상 모달 컴포넌트.
 * 광고 시청 플로우를 관리하고 토큰 보상을 처리합니다.
 */
import { ref, computed } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { Tv, Coins, CheckCircle, Loader2, X, AlertCircle, Play } from 'lucide-vue-next'

const store = useTesterStore()

/** 광고 시청 상태 */
const adState = ref<'idle' | 'loading' | 'watching' | 'success' | 'error'>('idle')

/** 에러 메시지 */
const errorMessage = ref('')

/** 획득한 토큰 */
const earnedTokens = ref(0)

/** 남은 광고 횟수 */
const remainingAds = computed(() => store.tokenInfo.daily_ad_remaining)

/** 모달 닫기 */
const close = () => {
    store.showAdRewardModal = false
    adState.value = 'idle'
    errorMessage.value = ''
    earnedTokens.value = 0
}

/**
 * 광고 시청 및 보상 요청을 처리합니다.
 * 실제 광고 SDK 연동 시 이 함수 내부를 수정합니다.
 */
const watchAd = async () => {
    if (remainingAds.value <= 0) return

    adState.value = 'loading'
    errorMessage.value = ''

    try {
        // 고유 트랜잭션 ID 생성 (Idempotency 보장)
        const transactionId = `ad_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`

        // TODO: 실제 광고 SDK 호출
        // 현재는 바로 보상 요청 (광고 SDK 연동 후 콜백에서 호출하도록 변경)
        adState.value = 'watching'

        // 시뮬레이션: 광고 시청 대기 (실제 구현 시 SDK 콜백으로 대체)
        await new Promise(resolve => setTimeout(resolve, 1500))

        // 서버에 보상 요청
        const res = await fetch('/api/ads/reward', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${store.userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ad_network: 'admob',
                transaction_id: transactionId,
                timestamp: Math.floor(Date.now() / 1000)
            })
        })

        if (res.ok) {
            const data = await res.json()
            earnedTokens.value = data.added_tokens
            store.tokenInfo.current_tokens = data.current_tokens
            store.tokenInfo.daily_ad_remaining = Math.max(0, store.tokenInfo.daily_ad_remaining - 1)
            adState.value = 'success'
        } else if (res.status === 429) {
            errorMessage.value = '오늘의 광고 시청 한도에 도달했습니다.'
            adState.value = 'error'
        } else if (res.status === 409) {
            errorMessage.value = '이미 처리된 보상 요청입니다.'
            adState.value = 'error'
        } else {
            errorMessage.value = '보상 처리에 실패했습니다. 다시 시도해주세요.'
            adState.value = 'error'
        }
    } catch (err) {
        errorMessage.value = '네트워크 오류가 발생했습니다.'
        adState.value = 'error'
    }
}

/** 성공 후 다시 시청할 수 있도록 리셋 */
const resetState = () => {
    adState.value = 'idle'
    earnedTokens.value = 0
}
</script>

<template>
    <Teleport to="body">
        <Transition name="modal">
            <div
                v-if="store.showAdRewardModal"
                class="fixed inset-0 z-50 flex items-center justify-center p-4"
            >
                <!-- Backdrop -->
                <div
                    class="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    @click="close"
                ></div>

                <!-- Modal -->
                <div class="relative w-full max-w-sm bg-gray-900 border border-gray-700/50 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden">
                    <!-- Header gradient -->
                    <div class="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-500"></div>

                    <div class="p-6 space-y-5">
                        <!-- Header -->
                        <div class="flex items-start justify-between">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                                    <Tv class="w-5 h-5 text-emerald-400" />
                                </div>
                                <div>
                                    <h3 class="text-base font-bold text-white">광고로 토큰 받기</h3>
                                    <p class="text-xs text-gray-400 mt-0.5">짧은 광고를 시청하고 토큰을 획득하세요</p>
                                </div>
                            </div>
                            <button
                                @click="close"
                                class="p-1 text-gray-500 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                            >
                                <X class="w-4 h-4" />
                            </button>
                        </div>

                        <!-- 현재 토큰 요약 -->
                        <div class="bg-gray-800/50 rounded-xl p-4 flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <Coins class="w-4 h-4 text-amber-400" />
                                <span class="text-sm text-gray-300">보유 토큰</span>
                            </div>
                            <span class="text-lg font-bold text-white tabular-nums">{{ store.tokenInfo.current_tokens }}</span>
                        </div>

                        <!-- Idle State -->
                        <div v-if="adState === 'idle'" class="space-y-3">
                            <button
                                @click="watchAd"
                                :disabled="remainingAds <= 0"
                                class="w-full h-12 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all flex items-center justify-center space-x-2 shadow-lg shadow-emerald-500/20 active:scale-[0.98]"
                            >
                                <Play class="w-5 h-5" />
                                <span>광고 시청 (+5 토큰)</span>
                            </button>
                            <p class="text-center text-[10px] text-gray-500">
                                오늘 남은 횟수: <span class="text-emerald-400 font-semibold">{{ remainingAds }}회</span>
                            </p>
                        </div>

                        <!-- Loading/Watching State -->
                        <div v-else-if="adState === 'loading' || adState === 'watching'" class="flex flex-col items-center space-y-3 py-4">
                            <Loader2 class="w-8 h-8 text-emerald-400 animate-spin" />
                            <p class="text-sm text-gray-300">
                                {{ adState === 'loading' ? '광고를 불러오는 중...' : '광고를 시청 중...' }}
                            </p>
                        </div>

                        <!-- Success State -->
                        <div v-else-if="adState === 'success'" class="flex flex-col items-center space-y-4 py-2">
                            <div class="w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center">
                                <CheckCircle class="w-8 h-8 text-emerald-400" />
                            </div>
                            <div class="text-center">
                                <p class="text-lg font-bold text-white">+{{ earnedTokens }} 토큰 획득!</p>
                                <p class="text-xs text-gray-400 mt-1">현재 잔액: {{ store.tokenInfo.current_tokens }} 토큰</p>
                            </div>
                            <div class="flex space-x-2 w-full">
                                <button
                                    v-if="remainingAds > 0"
                                    @click="resetState"
                                    class="flex-1 h-10 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-all"
                                >
                                    한 번 더 시청
                                </button>
                                <button
                                    @click="close"
                                    class="flex-1 h-10 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm rounded-xl transition-all"
                                >
                                    닫기
                                </button>
                            </div>
                        </div>

                        <!-- Error State -->
                        <div v-else-if="adState === 'error'" class="flex flex-col items-center space-y-3 py-2">
                            <div class="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                                <AlertCircle class="w-6 h-6 text-red-400" />
                            </div>
                            <p class="text-sm text-red-300 text-center">{{ errorMessage }}</p>
                            <button
                                @click="resetState"
                                class="w-full h-10 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm rounded-xl transition-all"
                            >
                                다시 시도
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.2s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
    transition: transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}
.modal-enter-from .relative {
    transform: scale(0.95) translateY(10px);
}
</style>
