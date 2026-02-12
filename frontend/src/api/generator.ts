import type { GenerateRequest, SSEChunk } from './types'

/**
 * 코드 생성 API 서비스
 */

/**
 * 테스트 코드를 생성합니다 (스트리밍).
 *
 * @param params 생성 요청 매개변수 (코드, 언어, 모델 등).
 * @param token 인증 토큰.
 * @param onChunk 청크 수신 시 호출될 콜백 함수.
 * @param onError 에러 발생 시 호출될 콜백 함수.
 * @throws Error API 요청 실패 또는 유효성 검사 오류 시.
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
            // 에러 메시지 추출 간소화
            errorMessage = errorData.detail?.message || errorData.detail || errorData.message || response.statusText || errorMessage
        } catch (e) {
            // 기본 메시지 유지
        }
        throw new Error(errorMessage)
    }

    // 200 OK이지만 유효성 검사 오류인 경우 처리 (콘솔 오류 방지)
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
                // 이벤트 타입 라인 (현재는 사용하지 않으나, 향후 확장을 위해 유지)
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
                    // JSON이 아닌 경우 평문으로 처리
                    onChunk(dataStr)
                }
            }
        }
    }
}

/**
 * 생성된 테스트 코드를 실행합니다.
 *
 * @param inputCode 원본 소스 코드.
 * @param testCode 실행할 테스트 코드.
 * @param language 프로그래밍 언어.
 * @param token 인증 토큰.
 * @returns 실행 결과 객체.
 * @throws Error 실행 요청 실패 시.
 */
export async function executeTestCode(inputCode: string, testCode: string, language: string, token: string): Promise<any> {
    const response = await fetch('/api/execution/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ code: inputCode, test_code: testCode, language })
    })

    if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`)
    }

    return await response.json()
}

/**
 * 사용자의 생성 이력을 조회합니다.
 *
 * @param token 인증 토큰.
 * @returns 생성 이력 목록.
 */
export async function fetchHistory(token: string): Promise<any[]> {
    const response = await fetch('/api/history/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    if (!response.ok) {
        return []
    }

    return await response.json()
}
