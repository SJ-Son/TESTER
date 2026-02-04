/**
 * Domain Models and Business Logic Types
 */
import type { SupportedLanguage, GeminiModel } from './api.types'

export type { SupportedLanguage, GeminiModel }

export interface HistoryItem {
    id: number
    timestamp: string
    inputCode: string
    result: string
    language: SupportedLanguage
}

export interface LanguageOption {
    value: SupportedLanguage
    label: string
    icon: string
}

export interface ModelOption {
    value: GeminiModel
    label: string
    description: string
}

export interface TestGenerationOptions {
    code: string
    language: SupportedLanguage
    model?: GeminiModel
    turnstileToken: string
}

export interface TestGenerationResult {
    isGenerating: boolean
    result: string
    error: string | null
}
