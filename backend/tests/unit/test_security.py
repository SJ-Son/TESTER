import pytest
from cryptography.fernet import Fernet
from src.exceptions import DecryptionError, EncryptionError
from src.utils.security import EncryptionService
from src.config.settings import settings

# Mock settings for testing
@pytest.fixture
def mock_settings(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "DATA_ENCRYPTION_KEY", key)
    return key

class TestEncryptionService:
    def test_init_success(self, mock_settings):
        service = EncryptionService()
        assert isinstance(service.cipher, Fernet)

    def test_init_missing_key(self, monkeypatch):
        monkeypatch.setattr(settings, "DATA_ENCRYPTION_KEY", None)
        with pytest.raises(ValueError, match="DATA_ENCRYPTION_KEY must be set"):
            EncryptionService()

    def test_init_invalid_key(self, monkeypatch):
        monkeypatch.setattr(settings, "DATA_ENCRYPTION_KEY", "invalid_key")
        with pytest.raises(ValueError, match="Invalid DATA_ENCRYPTION_KEY"):
            EncryptionService()

    def test_encrypt_decrypt_success(self, mock_settings):
        service = EncryptionService()
        data = "sensitive data"
        encrypted = service.encrypt(data)
        assert encrypted != data
        decrypted = service.decrypt(encrypted)
        assert decrypted == data

    def test_encrypt_empty(self, mock_settings):
        service = EncryptionService()
        assert service.encrypt("") == ""

    def test_decrypt_empty(self, mock_settings):
        service = EncryptionService()
        assert service.decrypt("") == ""

    def test_decrypt_failure(self, mock_settings):
        service = EncryptionService()
        with pytest.raises(DecryptionError, match="데이터 복호화 실패"):
            service.decrypt("invalid_token")

    def test_encrypt_failure(self, mock_settings):
        service = EncryptionService()
        # Mock cipher.encrypt to raise exception
        original_encrypt = service.cipher.encrypt
        def mock_encrypt(data):
            raise Exception("Encryption failed")
        service.cipher.encrypt = mock_encrypt

        with pytest.raises(EncryptionError, match="데이터 암호화 실패"):
            service.encrypt("data")
