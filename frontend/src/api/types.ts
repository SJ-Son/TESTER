/**
 * Type definitions for API requests and responses
 */

/**
 * @deprecated Import from @/types instead
 * This file is kept for backward compatibility
 */
export * from '../types/api.types'

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
