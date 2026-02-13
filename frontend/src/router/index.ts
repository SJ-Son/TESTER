import { createRouter, createWebHistory } from 'vue-router'

/**
 * Vue Router 설정
 * 애플리케이션의 라우팅 규칙을 정의합니다.
 */
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: { template: '' } // RouterView에 아무것도 렌더링하지 않음 (HomeView가 배경에 표시됨)
        },
        {
            path: '/privacy',
            name: 'privacy',
            component: () => import('../views/PrivacyPolicy.vue') // 지연 로드 (Lazy load)
        },
        {
            path: '/terms',
            name: 'terms',
            component: () => import('../views/TermsOfService.vue')
        },
        {
            path: '/changelog',
            name: 'changelog',
            component: () => import('../views/ChangelogView.vue')
        },
        {
            path: '/auth/callback',
            name: 'auth-callback',
            component: () => import('../views/AuthCallback.vue')
        }
    ]
})

export default router
