from collections.abc import AsyncGenerator

from src.exceptions import ValidationError
from src.languages.factory import LanguageFactory
from src.repositories.generation_repository import GenerationRepository
from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestGeneratorService:
    """
    테스트 코드 생성 비즈니스 로직을 담당하는 서비스

    역할:
    1. 언어별 전략 선택 및 검증
    2. Prompt 컨텍스트 생성
    3. AI 서비스 호출 (GeminiService)
    4. RAG 기반 Few-shot 예제 검색 및 프롬프트 주입
    """

    def __init__(self, gemini_service: GeminiService, generation_repository: GenerationRepository):
        self.gemini_service = gemini_service
        self.generation_repository = generation_repository

    async def generate_test(
        self, code: str, language: str, model: str, is_regenerate: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        테스트 코드를 생성합니다.

        Args:
            code: 소스 코드
            language: 프로그래밍 언어
            model: 사용할 AI 모델명

        Yields:
            str: 생성된 테스트 코드 청크 (스트리밍)

        Raises:
            ValidationError: 코드 검증 실패 시
        """
        # 1. 언어 전략 선택
        strategy = LanguageFactory.get_strategy(language)

        # 2. 코드 검증
        result = strategy.validate_code(code)
        if not result.is_valid:
            raise ValidationError(result.error_message)

        # 3. RAG: 임베딩 벡터 생성 및 우수 사례 검색
        few_shot_text = ""
        self.last_embedding = None
        try:
            embedding = await self.gemini_service.generate_embedding(code)
            if embedding:
                self.last_embedding = embedding
                similar_histories = (
                    await self.generation_repository.get_similar_successful_generations(
                        embedding=embedding, limit=2, language=language
                    )
                )

                if similar_histories:
                    examples = []
                    for h in similar_histories:
                        # 예시가 너무 길면 절삭 (방어 로직: 1500자 제한)
                        trunc_input = h.input_code[:750] + (
                            "..." if len(h.input_code) > 750 else ""
                        )
                        trunc_output = h.generated_code[:750] + (
                            "..." if len(h.generated_code) > 750 else ""
                        )
                        examples.append(
                            f"### Example\nInput Code:\n{trunc_input}\n\nGenerated Test:\n{trunc_output}"
                        )

                    few_shot_text = "\n\n".join(examples)
                    logger.info(
                        f"RAG: {len(similar_histories)}개의 우수 사례를 프롬프트에 주입합니다."
                    )
        except Exception as e:
            error_msg = str(e).replace('"', "'").replace("\n", " ")
            logger.warning(f"RAG Few-shot 예제 검색 중 오류 발생: {error_msg}")
            yield f'event: warning\ndata: {{"message": "RAG 임베딩 예외 발생: {error_msg} (코드는 계속 생성됩니다)"}}\n\n'
            
        # 4. 시스템 프롬프트 생성
        # strategy에 get_system_instruction이 few_shot_text 인자를 받도록 업데이트가 선행되거나
        # 여기에서 동적으로 문자열을 이어붙입니다.
        base_instruction = strategy.get_system_instruction()
        if few_shot_text:
            system_instruction = (
                f"{base_instruction}\n\n"
                f"### 참고용 우수 테스트 코드 사례 (Few-shot Examples)\n"
                f"다음은 이전에 생성하여 성공적으로 통과된 테스트 코드 예시입니다.\n"
                f"이 예시들의 스타일과 구조를 학습하여, 사용자 코드의 테스트를 생성해주세요:\n\n"
                f"{few_shot_text}"
            )
        else:
            system_instruction = base_instruction

        logger.info(f"생성할 프롬프트 시스템 지시문 길이: {len(system_instruction)}")

        # 5. 모델별 Gemini 서비스 인스턴스 가져오기
        gemini_service = GeminiService(model_name=model)

        # 6. AI 생성 호출 (캐싱은 GeminiService 내부에서 처리됨)
        async for chunk in gemini_service.generate_test_code(
            source_code=code,
            system_instruction=system_instruction,
            stream=True,
            is_regenerate=is_regenerate,
        ):
            yield chunk
