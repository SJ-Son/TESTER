// 서드파티 전역 객체에 대한 타입 선언
declare global {
    interface Window {
        turnstile?: {
            render: (element: string | HTMLElement, options: any) => string
            reset: (widgetId?: string) => void
            remove: (widgetId: string) => void
        }
    }
}

// Google 로그인 로직 제거됨 (Supabase Auth로 대체)

// Cloudflare Turnstile 지연 로드
let turnstileLoaded = false
let turnstilePromise: Promise<void> | null = null

/**
 * Cloudflare Turnstile 스크립트를 동적으로 로드합니다.
 *
 * @returns 로드 완료시 해결되는 Promise.
 */
export function loadTurnstile(): Promise<void> {
    if (typeof window.turnstile !== 'undefined') {
        turnstileLoaded = true
        return Promise.resolve()
    }

    if (turnstilePromise) {
        return turnstilePromise
    }

    turnstilePromise = new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
        script.async = true
        script.defer = true
        script.onload = () => {
            turnstileLoaded = true
            resolve()
        }
        script.onerror = () => reject(new Error('Turnstile 로드 실패'))
        document.head.appendChild(script)
    })

    return turnstilePromise
}
