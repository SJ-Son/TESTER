/**
 * Type definitions for API requests and responses
 */

export interface GenerateRequest {
    input_code: string
    language: string
    model: string
    turnstile_token: string
}

export interface SSEChunk {
    type: 'chunk' | 'error' | 'done'
    content?: string
    code?: string
    message?: string
}

export interface GoogleTokenRequest {
    id_token: string
}

export interface AuthResponse {
    access_token: string
    token_type: string
}

export interface ErrorResponse {
    code: string
    message: string
}
