"""
Gemini API 연동 서비스.
"""
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger
# from backend.src.utils.prompts import SYSTEM_INSTRUCTION


class GeminiService:
    """Gemini API를 통한 테스트 코드 생성 서비스"""

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.logger = get_logger(__name__)
        self.model_name = model_name
        self.logger = get_logger(__name__)
        self._configure_api()

    def _configure_api(self) -> None:
        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY 미설정")
            genai.configure(api_key=api_key)
        except Exception as e:
            self.logger.error(f"API 설정 실패: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def generate_test_code(self, source_code: str, system_instruction: str = None, stream: bool = True, use_reflection: bool = False):
        """
        Args:
            source_code: 테스트할 소스 코드
            system_instruction: 언어별 시스템 프롬프트
            stream: 스트리밍 여부 (True: Generator, False: str)
            use_reflection: (V3) 자기 성찰(Self-Correction) 사용 여부
        """
        if not source_code.strip():
            msg = "# 코드를 입력해주세요."
            if stream:
                yield msg
                return
            return msg

        try:
            # 동적으로 모델 인스턴스 생성
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            # 1. Draft 생성 (Reflection 모드면 스트림 끄기)
            # Reflection을 쓰려면 전체 초안이 필요하므로, 내부적으로는 stream=False로 받음
            if use_reflection:
                response = model.generate_content(source_code, stream=False)
                draft_code = response.text
                
                # 2. Reflection (검토 및 수정)
                final_code = self._reflect_and_refine(draft_code, system_instruction)
                
                # 3. 결과 반환
                if stream:
                    # 스트리밍 요청이었다면, 완성된 코드를 한 번에 yield (또는 청크로 나눌 수도 있음)
                    yield final_code
                else:
                    return final_code
            
            else:
                # 기존 로직
                response = model.generate_content(source_code, stream=stream)
            
                if stream:
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                else:
                    if not response.text:
                        return "# 응답 생성 실패"
                    return response.text
                
        except Exception as e:
            self.logger.error(f"API 호출 오류: {e}")
            raise

    def _reflect_and_refine(self, draft_code: str, context: str) -> str:
        """
        [V3 Feature] The Self-Corrector
        생성된 초안 코드를 검토하고, 문제가 있다면 수정합니다.
        
        Args:
            draft_code: AI가 생성한 초안 코드
            context: 원래의 시스템 프롬프트 (언어 맥락 파악용)
        Returns:
            수정된 코드 (문제가 없다면 초안 그대로)
        """
        reviewer_prompt = f"""
        당신은 [Strict Syntax Nazi] 입니다.
        
        [임무]
        아래의 코드(DRAFT)를 "매우 엄격하게" 검토하십시오.
        인사말, 칭찬, 부연 설명은 일체 생략하십시오.
        
        [검토 기준]
        1. 언어 혼용 오류: Java 코드에 Python 문법(def 등)이 있거나, JS 코드에 Java 문법이 섞여 있는지 확인.
        2. 문법적 결함: 해당 언어에서 실행 불가능한 구문 확인.
        3. 컨텍스트 일치: 원래 요청된 언어({context[:100]}...)와 일치하는지 확인.
        
        [출력 규칙]
        - 오류가 전혀 없다면 대소문자 구분 없이 오직 `PASS` 라고만 출력하십시오.
        - 오류가 있다면, 즉시 수정한 **전체 코드**만 출력하십시오. (코드 블록 ```...``` 사용)
        
        [DRAFT]
        {draft_code}
        """
        
        try:
            # 리뷰용 모델 (가장 똑똑한 모델 사용 권장)
            # 여기서는 편의상 동일 모델 사용
            reviewer = genai.GenerativeModel(
                model_name=self.model_name
            )
            report = reviewer.generate_content(reviewer_prompt).text.strip()
            
            if "PASS" in report.upper() and len(report) < 10:
                self.logger.info("Self-Reflection: PASS")
                return draft_code
            else:
                self.logger.info("Self-Reflection: REFINED code returned")
                return report
                
        except Exception as e:
            self.logger.warning(f"Self-Reflection Failed: {e}")
            return draft_code
                

