import logging

from src.repositories.generation_repository import GenerationRepository

logger = logging.getLogger(__name__)


def background_save_generation(
    repository: GenerationRepository,
    user_id: str,
    input_code: str,
    generated_code: str,
    language: str,
    model: str,
):
    """
    Background Task: Save generation history reliably.
    Executes after the response is sent, ensuring data persistence even if the client disconnects.
    """
    try:
        logger.info(f"[Background] Saving generation for user {user_id}...")
        result = repository.create_history(
            user_id=user_id,
            input_code=input_code,
            generated_code=generated_code,
            language=language,
            model=model,
        )
        if result:
            logger.info(f"[Background] Save Success. ID: {result.id}")
        else:
            logger.error("[Background] Save Failed: Repository returned None.")
    except Exception as e:
        logger.error(f"[Background] Save Error: {e}", exc_info=True)
