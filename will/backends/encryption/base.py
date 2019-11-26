class WillBaseEncryptionBackend(object):

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def encrypt_to_b64(raw):
        raise NotImplementedError

    @staticmethod
    def decrypt_from_b64(enc):
        raise NotImplementedError
