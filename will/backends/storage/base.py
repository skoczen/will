import logging
import redis
from six.moves.urllib.parse import urlparse
from will.mixins import SettingsMixin, EncryptionMixin


class BaseStorageBackend(SettingsMixin, EncryptionMixin, object):
    required_settings = []

    """
    The base storage backend.  All storage backends must supply the following methods:
    __init__() - sets up the connection
    save() - saves a single value to a key
    clear() - deletes a key
    clear_all_keys() - clears the db
    load() - gets a value from the backend
    """

    def backend_save(self, key, value, expire=None):
        raise NotImplemented

    def clear(self, key):
        raise NotImplemented

    def clear_all_keys(self):
        raise NotImplemented

    def backend_load(self, key):
        raise NotImplemented

    def save(self, key, value, *args, **kwargs):
        self.backend_save(key, self.encrypt(value), *args, **kwargs)

    def load(self, key, *args, **kwargs):
        try:
            return self.decrypt(self.backend_load(key, *args, **kwargs))
        except:
            logging.warn("Error decrypting.  Attempting unencrypted load for %s to ease migration." % key)
            return self.backend_load(key, *args, **kwargs)
