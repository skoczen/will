'Encrypt stored data'

import binascii
import hashlib
import logging
import os

import dill as pickle
from Crypto.Cipher import AES

from will import settings
from will.backends.encryption.base import WillBaseEncryptionBackend

# pylint: disable=no-member

BS = 16
key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def pad(s: bytes) -> str:
    '''Ensure the data to be encrypted has sufficient padding.
    Arbitrarily adding ~ to the end, so your message better not end with ~.'''
    return "%s%s" % (s.decode("utf-8"), ((BS - len(s) % BS) * "~"))


def unpad(s: bytes) -> bytes:
    'Removes all ~ on the end of the message.'
    return s.rstrip(b'~')


class AESEncryption(WillBaseEncryptionBackend):
    'AES encryption backend'
    @staticmethod
    def encrypt_to_b64(raw):
        'encrypt and b64-encode data'
        try:
            enc = binascii.b2a_base64(pickle.dumps(raw, -1))
            if settings.ENABLE_INTERNAL_ENCRYPTION:
                iv = binascii.b2a_hex(os.urandom(8))
                cipher = AES.new(key, AES.MODE_CBC, iv)
                enc = binascii.b2a_base64(cipher.encrypt(pad(enc)))
                return "%s/%s" % (iv.decode("utf-8"), enc.decode("utf-8"))
            return enc
        except Exception:
            logging.exception("Error preparing message for the wire: \n%s", raw)
            return None

    @staticmethod
    def decrypt_from_b64(enc):
        'decrypt b64-encoded data'
        try:
            if b'/' in enc and enc.index(b'/') == BS:
                iv = enc[:BS]
                encrypted_data = enc[BS+1:]
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted_data = unpad(cipher.decrypt(binascii.a2b_base64(encrypted_data)))
            return pickle.loads(binascii.a2b_base64(decrypted_data))
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception:
            logging.debug("Error decrypting.  Attempting unencrypted load to ease migration.")
            return pickle.loads(binascii.a2b_base64(enc))


def bootstrap(encryption_settings):
    'Returns the encryption module'
    return AESEncryption(encryption_settings)
