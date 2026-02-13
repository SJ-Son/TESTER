/**
 * 도메인 모델 및 비즈니스 로직 타입 정의
 */
import type { SupportedLanguage, GeminiModel } from './api.types'

export type { SupportedLanguage, GeminiModel }

/** 히스토리 아이템 인터페이스 */
export interface HistoryItem {
    id: number
    /** 생성 일시 */
    timestamp: string
    /** 입력 코드 */
    inputCode: string
    /** 생성 결과 (테스트 코드) */
    result: string
    /** 사용된 언어 */
    language: SupportedLanguage
}

/** 언어 선택 옵션 인터페이스 */
export interface LanguageOption {
    /** 언어 식별자 */
    value: SupportedLanguage
    /** 표시 라벨 */
    label: string
    /** 아이콘 식별자 */
    icon: string
}

/** 모델 선택 옵션 인터페이스 */
export interface ModelOption {
    /** 모델 식별자 */
    value: GeminiModel
    /** 표시 이름 */
    label: string
    /** 모델 설명 */
    description: string
}

/** 테스트 생성 옵션 인터페이스 */
export interface TestGenerationOptions {
    code: string
    language: SupportedLanguage
    model?: GeminiModel
    turnstileToken: string
}

/** 테스트 생성 결과 인터페이스 */
export interface TestGenerationResult {
    /** 생성 진행 중 여부 */
    isGenerating: boolean
    /** 생성된 결과 코드 */
    result: string
    /** 에러 메시지 (없으면 null) */
    error: string | null
}
