"""데이터 암호화/복호화 서비스.

AES 기반 Fernet 암호화를 사용하여 민감한 데이터를 보호합니다.
Fail-Closed 원칙: 암호화 키 누락 시 애플리케이션 시작 불가.
"""

from typing import Final

from cryptography.fernet import Fernet
from src.config.settings import settings
from src.exceptions import DecryptionError, EncryptionError
from src.types import EncryptedData
from src.utils.logger import get_logger


class EncryptionService:
    """AES/Fernet 기반 데이터 암호화/복호화 서비스.

    Fail-Closed 정책:
        - 암호화 키 누락 시 초기화 실패 (ValueError)
        - 암호화 실패 시 평문 반환 금지 (EncryptionError)
        - 복호화 실패 시 에러 전파 (DecryptionError)
    """

    def __init__(self) -> None:
        """EncryptionService 인스턴스를 초기화합니다.

        Raises:
            ValueError: DATA_ENCRYPTION_KEY가 설정되지 않았거나 잘못된 경우.
        """
        self.logger = get_logger(__name__)

        encryption_key = settings.DATA_ENCRYPTION_KEY
        if not encryption_key:
            self.logger.critical("DATA_ENCRYPTION_KEY 미설정으로 보안 시작 불가")
            raise ValueError("DATA_ENCRYPTION_KEY must be set in environment variables.")

        try:
            self.cipher: Final[Fernet] = Fernet(encryption_key)
        except Exception as e:
            self.logger.critical(f"잘못된 암호화 키 형식: {e}")
            raise ValueError(f"Invalid DATA_ENCRYPTION_KEY: {e}") from e

    def encrypt(self, data: str) -> EncryptedData:
        """문자열을 암호화합니다.

        Args:
            data: 암호화할 평문 문자열.

        Returns:
            암호화된 문자열.

        Raises:
            EncryptionError: 암호화 실패 시 (평문 반환 금지).
        """
        if not data:
            return EncryptedData(data)

        try:
            encrypted = self.cipher.encrypt(data.encode()).decode()
            return EncryptedData(encrypted)
        except Exception as e:
            self.logger.error(f"암호화 실패: {e}")
            raise EncryptionError("데이터 암호화 실패") from e

    def decrypt(self, token: str) -> str:
        """암호화된 문자열을 복호화합니다.

        Args:
            token: 암호화된 문자열.

        Returns:
            복호화된 평문 문자열.

        Raises:
            DecryptionError: 복호화 실패 시 (데이터 오염 가능성).
        """
        if not token:
            return token

        try:
            decrypted = self.cipher.decrypt(token.encode()).decode()
            return decrypted
        except Exception as e:
            self.logger.error(f"복호화 실패: {e}")
            raise DecryptionError("데이터 복호화 실패 (데이터 손상 또는 키 불일치)") from e
