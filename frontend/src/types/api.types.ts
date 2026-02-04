/**
 * API Request/Response Types
 */

// Shared types
export type SupportedLanguage = 'python' | 'javascript' | 'java'
export type GeminiModel = 'gemini-3-flash-preview'  // 실제 사용하는 모델만

export interface GenerateRequest {
    input_code: string
    language: SupportedLanguage
    model: GeminiModel
    turnstile_token: string
    is_regenerate?: boolean
}

export interface SSEChunk {
    type: 'chunk' | 'error' | 'done'
    content?: string
    message?: string
    code?: string
}

export interface GoogleAuthResponse {
    access_token: string
    token_type: string
    expires_in: number
    user: {
        id: string
        email: string
        name: string
        picture: string
    }
}

export interface HealthCheckResponse {
    status: 'ok' | 'error'
    timestamp: string
    version?: string
}
