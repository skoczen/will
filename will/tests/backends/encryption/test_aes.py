from will import settings
import pytest


@pytest.fixture()
def settings_secret_key():
    """Set settings.SECRET_KEY values"""
    settings.SECRET_KEY = "Top_secret"
    from will.backends.encryption.aes import AESEncryption
    converter = AESEncryption()

    return converter


class TestAESEncryption:

    def test_encrypt_to_b64(self, settings_secret_key):
        test_string = 'This is my test string'
        encrypted_string = settings_secret_key.encrypt_to_b64(test_string)
        print(encrypted_string)

        assert test_string is not encrypted_string

    def test_decrypt_from_b64(self, settings_secret_key):
        test_string = 'This is my test string'
        encrypted_string = settings_secret_key.encrypt_to_b64(test_string)
        decrypted_string = settings_secret_key.decrypt_from_b64(encrypted_string)
        assert decrypted_string == test_string
        print(encrypted_string)

        assert test_string == decrypted_string
