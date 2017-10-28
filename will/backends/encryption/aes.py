import binascii
import base64
import codecs
import dill as pickle
import hashlib
import logging
from Crypto.Cipher import AES
import random
import os
import traceback

from will import settings
from will.backends.encryption.base import WillBaseEncryptionBackend


BS = 16
key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def pad(s):
    s = "%s%s" % (s.decode("utf-8"), ((BS - len(s) % BS) * "~"))
    return s


def unpad(s):
    while s.endswith(str.encode("~")):
        s = s[:-1]
    return s


class AESEncryption(WillBaseEncryptionBackend):

    @classmethod
    def encrypt_to_b64(cls, raw):
        try:
            enc = binascii.b2a_base64(pickle.dumps(raw, -1))
            if settings.ENABLE_INTERNAL_ENCRYPTION:
                iv = binascii.b2a_hex(os.urandom(8))
                cipher = AES.new(key, AES.MODE_CBC, iv)
                enc = binascii.b2a_base64(cipher.encrypt(pad(enc)))
                return "%s/%s" % (iv.decode("utf-8"), enc.decode("utf-8"))
            else:
                return enc
        except:
            logging.critical("Error preparing message for the wire: \n%s" % traceback.format_exc())
            return None

    @classmethod
    def decrypt_from_b64(cls, raw_enc):
        try:
            if settings.ENABLE_INTERNAL_ENCRYPTION:
                iv = raw_enc[:BS]
                enc = raw_enc[BS+1:]
                cipher = AES.new(key, AES.MODE_CBC, iv)
                enc = unpad(cipher.decrypt(binascii.a2b_base64(enc)))
            return pickle.loads(binascii.a2b_base64(enc))
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.warn("Error decrypting.  Attempting unencrypted load to ease migration.")
            return pickle.loads(binascii.a2b_base64(raw_enc))


def bootstrap(settings):
    return AESEncryption(settings)
