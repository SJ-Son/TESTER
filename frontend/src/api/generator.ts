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
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Failed to connect to server')
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
