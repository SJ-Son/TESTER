/**
 * API 요청/응답 타입 정의
 */

// 공통 타입
/** 지원하는 프로그래밍 언어 */
export type SupportedLanguage = 'python' | 'javascript' | 'java'
/** 사용 가능한 Gemini 모델 */
export type GeminiModel = 'gemini-3-flash-preview'  // 실제 사용하는 모델만

/** 코드 생성 요청 인터페이스 */
export interface GenerateRequest {
    /** 사용자가 입력한 소스 코드 */
    input_code: string
    /** 대상 프로그래밍 언어 */
    language: SupportedLanguage
    /** 사용할 모델 식별자 */
    model: GeminiModel
    /** Cloudflare Turnstile 검증 토큰 */
    turnstile_token: string
    /** 재생성 요청 여부 */
    is_regenerate?: boolean
}

/** SSE(Server-Sent Events) 청크 데이터 인터페이스 */
export interface SSEChunk {
    /** 이벤트 타입 ('chunk': 데이터, 'error': 에러, 'done': 완료) */
    type: 'chunk' | 'error' | 'done'
    /** 생성된 코드 조각 (chunk 타입일 때) */
    content?: string
    /** 에러 메시지 (error 타입일 때) */
    message?: string
    /** 에러 코드 */
    code?: string
}

/** 구글 인증 응답 인터페이스 */
export interface GoogleAuthResponse {
    /** 액세스 토큰 */
    access_token: string
    /** 토큰 타입 (보통 'Bearer') */
    token_type: string
    /** 만료 시간 (초) */
    expires_in: number
    /** 사용자 정보 */
    user: {
        id: string
        email: string
        name: string
        picture: string
    }
}

/** 헬스 체크 응답 인터페이스 */
export interface HealthCheckResponse {
    /** 상태 ('ok' 또는 'error') */
    status: 'ok' | 'error'
    /** 타임스탬프 (ISO 8601) */
    timestamp: string
    /** 서비스 버전 */
    version?: string
}

// === 토큰 시스템 타입 ===

/** 토큰 정보 인터페이스 */
export interface TokenInfo {
    /** 현재 보유 토큰 */
    current_tokens: number
    /** 금일 로그인 보너스 수령 여부 */
    daily_bonus_claimed: boolean
    /** 테스트 1회 생성 비용 */
    cost_per_generation: number
}

/** 사용자 상태 API 응답 */
export interface UserStatusResponse {
    user: {
        id: string
        email: string | null
    }
    token_info: TokenInfo
    /** @deprecated quota 필드는 하위 호환성을 위해 유지, token_info 사용 권장 */
    quota?: {
        limit: number
        used: number
        remaining: number
    }
}

/** 토큰 부족 에러 응답 (HTTP 402) */
export interface InsufficientTokensErrorResponse {
    detail: {
        code: 'INSUFFICIENT_TOKENS'
        message: string
        required: number
        current: number
    }
}
