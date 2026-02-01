import type { GoogleTokenRequest, AuthResponse } from './types'

/**
 * Authentication API service
 */

export async function loginWithGoogle(idToken: string): Promise<AuthResponse> {
    const response = await fetch('/api/auth/google', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_token: idToken } as GoogleTokenRequest)
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail?.message || 'Login failed')
    }

    return await response.json()
}
