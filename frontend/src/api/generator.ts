import type { GenerateRequest, SSEChunk } from './types'

/**
 * Code generation API service
 */

export async function generateTestCode(
    params: GenerateRequest,
    token: string,
    onChunk: (chunk: string) => void,
    onError: (error: string) => void
): Promise<void> {
    const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(params)
    })

    if (!response.ok) {
        let errorMessage = '서버 연결에 실패했습니다'
        try {
            const errorData = await response.json()
            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail
                } else if (errorData.detail.message) {
                    errorMessage = errorData.detail.message
                } else if (Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map((e: any) => e.msg).join(', ')
                }
            }
        } catch (e) {
            errorMessage = `에러 발생 (Status ${response.status})`
        }
        throw new Error(errorMessage)
    }

    // Handle 200 OK but with validation error (to keep console clean)
    const contentType = response.headers.get('Content-Type')
    if (contentType?.includes('application/json')) {
        const data = await response.json()
        if (data.type === 'error' && data.status === 'validation_error') {
            throw new Error(data.detail?.message || data.message || '입력 코드를 확인해주세요')
        }
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No stream available')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
            if (line.startsWith('event:')) {
                // Event type line (currently not used, but available for future)
                continue
            }

            if (line.startsWith('data:')) {
                const dataStr = line.substring(5).trim()
                try {
                    const data: SSEChunk = JSON.parse(dataStr)

                    if (data.type === 'chunk' && data.content) {
                        onChunk(data.content)
                    } else if (data.type === 'error') {
                        onError(data.message || 'Generation failed')
                        break
                    } else if (data.type === 'done') {
                        break
                    }
                } catch (e) {
                    // Fallback to plain text if not JSON
                    onChunk(dataStr)
                }
            }
        }
    }
}
