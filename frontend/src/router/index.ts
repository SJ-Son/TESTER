import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: { template: '' } // Renders nothing in RouterView, showing only background HomeView
        },
        {
            path: '/privacy',
            name: 'privacy',
            component: () => import('../views/PrivacyPolicy.vue') // Lazy load
        },
        {
            path: '/terms',
            name: 'terms',
            component: () => import('../views/TermsOfService.vue') // Lazy load
        },
        {
            path: '/changelog',
            name: 'changelog',
            component: () => import('../views/ChangelogView.vue') // Lazy load
        }
    ]
})

export default router
