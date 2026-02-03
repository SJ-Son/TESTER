import { ref, type Ref } from 'vue'

export interface TestGenerationOptions {
    code: string
    language: string
    model?: string
    turnstileToken: string
}

export interface TestGenerationResult {
    isGenerating: Ref<boolean>
    result: Ref<string>
    error: Ref<string | null>
    generate: (options: TestGenerationOptions) => Promise<void>
    reset: () => void
}

/**
 * 테스트 코드 생성 로직을 캡슐화한 Composable
 */
export function useTestGeneration(): TestGenerationResult {
    const isGenerating = ref(false)
    const result = ref('')
    const error = ref<string | null>(null)

    const generate = async (options: TestGenerationOptions) => {
        isGenerating.value = true
        error.value = null
        result.value = ''

        try {
            const response = await fetch('/api/v1/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                },
                body: JSON.stringify({
                    input_code: options.code,
                    language: options.language,
                    model: options.model || 'gemini-3-flash-preview',
                    turnstile_token: options.turnstileToken
                })
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            const reader = response.body?.getReader()
            if (!reader) {
                throw new Error('Response body is not readable')
            }

            const decoder = new TextDecoder()

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)
                const lines = chunk.split('\n')

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6))
                        if (data.type === 'chunk') {
                            result.value += data.content
                        } else if (data.type === 'error') {
                            throw new Error(data.message)
                        }
                    }
                }
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Unknown error'
            console.error('Test generation failed:', err)
        } finally {
            isGenerating.value = false
        }
    }

    const reset = () => {
        result.value = ''
        error.value = null
        isGenerating.value = false
    }

    return {
        isGenerating,
        result,
        error,
        generate,
        reset
    }
}
