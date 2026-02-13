/**
 * Vue 애플리케이션 진입점 (Entry Point).
 * Pinia 스토어와 Router를 설정하고 앱을 마운트합니다.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'

import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
