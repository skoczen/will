import importlib
import logging
import dill as pickle
import functools
from will import settings


class EncryptionMixin(object):
    @property
    def encryption_backend(self):
        if not hasattr(self, "_encryption"):
            if hasattr(self, "bot") and hasattr(self.bot, "_encryption"):
                self._encryption = self.bot._encryption
            else:
                # The ENCRYPTION_BACKEND setting points to a specific module namespace
                # aes => will.encryption.aes
                module_name = ''.join([
                    'will.backends.encryption.',
                    getattr(settings, 'ENCRYPTION_BACKEND', 'aes'),
                ])
                encryption_module = importlib.import_module(module_name)
                self._encryption = encryption_module.bootstrap(settings)
        return self._encryption

    def encrypt(self, raw):
        return self.encryption_backend.encrypt_to_b64(raw)

    def decrypt(self, enc):
        if enc:
            return self.encryption_backend.decrypt_from_b64(enc)
        return None
