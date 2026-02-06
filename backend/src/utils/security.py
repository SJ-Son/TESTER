from cryptography.fernet import Fernet
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """데이터 암호화/복호화 서비스 (AES/Fernet)"""

    def __init__(self):
        self.key = settings.DATA_ENCRYPTION_KEY
        if not self.key:
            # Fail-Closed: 키가 없으면 앱 구동 불가
            logger.critical("Data Encryption Key is missing! Application cannot start securely.")
            raise ValueError("DATA_ENCRYPTION_KEY must be set in environment variables.")

        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            # 키 형식이 잘못된 경우 등
            logger.critical(f"Invalid Data Encryption Key: {e}")
            raise ValueError(f"Invalid DATA_ENCRYPTION_KEY: {e}") from e

    def encrypt(self, data: str) -> str:
        """문자열 암호화 (Fail-Closed)"""
        if not data:
            return data

        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            # 암호화 실패 시 절대 평문 반환 금지
            logger.error(f"Encryption failed for data: {e}")
            raise RuntimeError("Encryption failed") from e

    def decrypt(self, token: str) -> str:
        """암호화된 문자열 복호화 (Fail-Closed)"""
        if not token:
            return token

        try:
            return self.cipher.decrypt(token.encode()).decode()
        except Exception as e:
            # 복호화 실패 시 에러 전파 (데이터 오염 가능성)
            logger.error(f"Decryption failed: {e}")
            raise RuntimeError("Decryption failed") from e
