import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PrivacyPolicy from '../views/PrivacyPolicy.vue'
import TermsOfService from '../views/TermsOfService.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/privacy',
            name: 'privacy',
            component: PrivacyPolicy
        },
        {
            path: '/terms',
            name: 'terms',
            component: TermsOfService
        }
    ]
})

export default router
