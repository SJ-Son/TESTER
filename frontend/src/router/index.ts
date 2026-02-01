import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PrivacyPolicy from '../views/PrivacyPolicy.vue'
import TermsOfService from '../views/TermsOfService.vue'
import ChangelogView from '../views/ChangelogView.vue'

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
        },
        {
            path: '/changelog',
            name: 'changelog',
            component: ChangelogView
        }
    ]
})

export default router
