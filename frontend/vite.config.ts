import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        fs: {
            // Allow serving files from one level up to the project root
            allow: ['..']
        },
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    },
    build: {
        cssCodeSplit: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    // 벤더 라이브러리 분리
                    'vendor-vue': ['vue', 'vue-router', 'pinia'],
                    'vendor-ui': ['lucide-vue-next'],
                    'vendor-markdown': ['marked', 'highlight.js'],
                    'vendor-utils': ['lodash']
                }
            }
        },
        // 청크 크기 경고 임계값
        chunkSizeWarningLimit: 600,
        // CSS 압축
        cssMinify: 'lightningcss',
        // Terser 압축 옵션
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,      // 프로덕션에서 console.log 제거
                drop_debugger: true,     // debugger 문 제거
                pure_funcs: ['console.log', 'console.info']
            }
        },
        // 소스맵 생성 (프로덕션에서는 비활성화)
        sourcemap: false,
        target: 'es2015'
    },
    css: {
        devSourcemap: false
    }
})
