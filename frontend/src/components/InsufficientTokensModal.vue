<script setup lang="ts">
/**
 * 토큰 부족 시 표시되는 모달 컴포넌트.
 * Ko-fi를 통한 토큰 충전을 유도합니다.
 */
import { computed } from 'vue'
import { useTesterStore } from '../stores/testerStore'
import { AlertTriangle, X } from 'lucide-vue-next'

const store = useTesterStore()

/** 생성에 필요한 토큰 수 */
const requiredTokens = computed(() => store.tokenInfo.cost_per_generation)

/** 부족한 토큰 수 */
const shortfall = computed(() =>
    Math.max(0, requiredTokens.value - store.tokenInfo.current_tokens)
)

/** 모달 닫기 */
const close = () => {
    store.showInsufficientTokensModal = false
}
</script>

<template>
    <Teleport to="body">
        <Transition name="modal">
            <div
                v-if="store.showInsufficientTokensModal"
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
                    <div class="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-amber-500 via-red-500 to-amber-500"></div>

                    <div class="p-6 space-y-5">
                        <!-- Icon & Title -->
                        <div class="flex items-start justify-between">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
                                    <AlertTriangle class="w-5 h-5 text-red-400" />
                                </div>
                                <div>
                                    <h3 class="text-base font-bold text-white">토큰이 부족합니다</h3>
                                    <p class="text-xs text-gray-400 mt-0.5">테스트 생성에 필요한 토큰이 부족합니다</p>
                                </div>
                            </div>
                            <button
                                @click="close"
                                class="p-1 text-gray-500 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                            >
                                <X class="w-4 h-4" />
                            </button>
                        </div>

                        <!-- Token Info -->
                        <div class="bg-gray-800/50 rounded-xl p-4 space-y-3">
                            <div class="flex justify-between items-center text-sm">
                                <span class="text-gray-400">보유 토큰</span>
                                <span class="font-bold text-red-400 tabular-nums">{{ store.tokenInfo.current_tokens }}</span>
                            </div>
                            <div class="flex justify-between items-center text-sm">
                                <span class="text-gray-400">필요 토큰</span>
                                <span class="font-bold text-white tabular-nums">{{ requiredTokens }}</span>
                            </div>
                            <div class="border-t border-gray-700/50 pt-2 flex justify-between items-center text-sm">
                                <span class="text-gray-400">부족분</span>
                                <span class="font-bold text-amber-400 tabular-nums">{{ shortfall }}</span>
                            </div>
                        </div>

                        <!-- Options -->
                        <div class="space-y-4">
                            <div class="p-4 bg-gray-800 rounded-xl text-center border border-gray-700">
                                <p class="text-sm text-gray-300 font-medium">토큰 결제 서비스 준비 중입니다</p>
                                <p class="text-xs text-gray-500 mt-1">문의: sjson666@gmail.com</p>
                            </div>

                            <button
                                @click="close"
                                class="w-full h-11 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-xl transition-all"
                            >
                                닫기
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
