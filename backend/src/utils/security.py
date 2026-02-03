from cryptography.fernet import Fernet

from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """데이터 암호화/복호화 서비스 (AES/Fernet)"""

    def __init__(self):
        self.key = settings.DATA_ENCRYPTION_KEY
        if self.key:
            try:
                self.cipher = Fernet(self.key)
            except Exception as e:
                logger.error(f"Invalid encryption key: {e}")
                self.cipher = None
        else:
            logger.warning("Encryption key not set. Data will be stored in plain text.")
            self.cipher = None

    def encrypt(self, data: str) -> str:
        """문자열 암호화"""
        if not self.cipher or not data:
            return data
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data

    def decrypt(self, token: str) -> str:
        """암호화된 문자열 복호화"""
        if not self.cipher or not token:
            return token
        try:
            return self.cipher.decrypt(token.encode()).decode()
        except Exception as e:
            logger.warning(f"Decryption failed (might be plain text): {e}")
            return token
