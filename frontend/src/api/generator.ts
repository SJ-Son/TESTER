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
        let errorMessage = `에러 발생 (Status ${response.status})`
        try {
            const errorData = await response.json()
            // Simplified error extraction
            errorMessage = errorData.detail?.message || errorData.detail || errorData.message || response.statusText || errorMessage
        } catch (e) {
            // keep default
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

export async function executeTestCode(inputCode: string, testCode: string, language: string, token: string): Promise<any> {
    const response = await fetch('/api/execution/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ input_code: inputCode, test_code: testCode, language })
    })

    if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`)
    }

    return await response.json()
}

export async function fetchHistory(token: string): Promise<any[]> {
    const response = await fetch('/api/history/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    if (!response.ok) {
        console.error(`History fetch failed: ${response.status} ${response.statusText}`)
        // Return empty array to avoid breaking the UI for now, but logged for debugging
        return []
    }

    return await response.json()
}
