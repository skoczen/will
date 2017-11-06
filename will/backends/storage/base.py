import logging
import redis
from six.moves.urllib.parse import urlparse
from will.mixins import SettingsMixin, EncryptionMixin


class PrivateBaseStorageBackend(SettingsMixin, EncryptionMixin, object):
    required_settings = []

    def save(self, key, value, *args, **kwargs):
        self.do_save(key, self.encrypt(value), *args, **kwargs)

    def load(self, key, *args, **kwargs):
        try:
            return self.decrypt(self.do_load(key, *args, **kwargs))
        except:
            logging.warn("Error decrypting.  Attempting unencrypted load for %s to ease migration." % key)
            return self.do_load(key, *args, **kwargs)


class BaseStorageBackend(PrivateBaseStorageBackend):
    """
    The base storage backend.  All storage backends must supply the following methods:
    __init__() - sets up the connection
    do_save() - saves a single value to a key
    do_load() - gets a value from the backend
    clear() - deletes a key
    clear_all_keys() - clears the db
    """

    def do_save(self, key, value, expire=None):
        raise NotImplemented

    def do_load(self, key):
        raise NotImplemented

    def clear(self, key):
        raise NotImplemented

    def clear_all_keys(self):
        raise NotImplemented
