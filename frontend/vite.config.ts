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
    build: {
        cssCodeSplit: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ['vue', 'vue-router'],
                },
            },
        },
        cssMinify: 'lightningcss',
        minify: 'esbuild',
        target: 'es2015',
    },
    esbuild: {
        drop: ['console', 'debugger'],
    },
    css: {
        devSourcemap: false,
    },
    server: {
        fs: {
            // Allow serving files from one level up to the project root
            allow: ['..'],
        },
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
})
