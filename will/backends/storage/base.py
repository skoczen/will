import redis
import urlparse
from will.mixins import SettingsMixin


class BaseStorageBackend(SettingsMixin, object):
    required_settings = []

    """
    The base storage backend.  All storage backends must supply the following methods:
    __init__() - sets up the connection
    save() - saves a single value to a key
    clear() - deletes a key
    clear_all_keys() - clears the db
    load() - gets a value from the backend
    """

    def save(self, key, value, expire=None):
        raise NotImplemented

    def clear(self, key):
        raise NotImplemented

    def clear_all_keys(self):
        raise NotImplemented

    def load(self, key):
        raise NotImplemented
