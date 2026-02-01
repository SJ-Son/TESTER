import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

import viteCompression from 'vite-plugin-compression'

export default defineConfig({
    plugins: [vue(), viteCompression()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
})
