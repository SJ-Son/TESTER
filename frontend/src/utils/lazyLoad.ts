// Type declarations for third-party global objects
declare global {
    interface Window {
        google?: {
            accounts: {
                id: {
                    initialize: (config: any) => void
                    renderButton: (element: HTMLElement | null, options: any) => void
                }
            }
        }
        turnstile?: {
            render: (element: string | HTMLElement, options: any) => string
            reset: (widgetId?: string) => void
            remove: (widgetId: string) => void
        }
    }
}

// Lazy load Google Sign-In
let googleSignInLoaded = false
let googleSignInPromise: Promise<void> | null = null

export function loadGoogleSignIn(): Promise<void> {
    if (googleSignInLoaded && typeof window.google !== 'undefined' && window.google.accounts) {
        return Promise.resolve()
    }

    if (googleSignInPromise) {
        return googleSignInPromise
    }

    googleSignInPromise = new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://accounts.google.com/gsi/client'
        script.async = true
        script.defer = true
        script.onload = () => {
            googleSignInLoaded = true
            resolve()
        }
        script.onerror = () => reject(new Error('Failed to load Google Sign-In'))
        document.head.appendChild(script)
    })

    return googleSignInPromise
}

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
