/**
 * API 요청 및 응답에 대한 타입 정의
 */

/**
 * @deprecated @/types에서 가져오십시오.
 * 이 파일은 하위 호환성을 위해 유지됩니다.
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
