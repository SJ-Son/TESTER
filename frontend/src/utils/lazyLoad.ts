// Type declarations for third-party global objects
declare global {
    interface Window {
        turnstile?: {
            render: (element: string | HTMLElement, options: any) => string
            reset: (widgetId?: string) => void
            remove: (widgetId: string) => void
        }
    }
}

// Google Sign-In logic removed (Replaced by Supabase Auth)

// Lazy load Cloudflare Turnstile
let turnstileLoaded = false
let turnstilePromise: Promise<void> | null = null

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
        script.onerror = () => reject(new Error('Failed to load Turnstile'))
        document.head.appendChild(script)
    })

    return turnstilePromise
}
