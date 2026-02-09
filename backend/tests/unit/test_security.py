"""Security utils 단위 테스트 - 간단 버전."""

from unittest.mock import patch

from src.utils.security import EncryptionService


def test_encryption_service_init():
    """EncryptionService 초기화 테스트."""
    with patch.dict(
        "os.environ",
        {"DATA_ENCRYPTION_KEY": "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleTE="},
        clear=False,
    ):
        service = EncryptionService()
        assert service is not None
        assert service.cipher is not None


def test_encrypt_decrypt_roundtrip():
    """암호화 후 복호화 시 원본 복원."""
    with patch.dict(
        "os.environ",
        {"DATA_ENCRYPTION_KEY": "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleTE="},
        clear=False,
    ):
        service = EncryptionService()
        plaintext = "Hello, World!"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext


def test_encrypt_unicode():
    """유니코드 문자열 암호화/복호화."""
    with patch.dict(
        "os.environ",
        {"DATA_ENCRYPTION_KEY": "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleTE="},
        clear=False,
    ):
        service = EncryptionService()
        plaintext = "안녕하세요! 🎉"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext
