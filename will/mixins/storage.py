import importlib
import logging
import dill as pickle
import functools
from will import settings


class StorageMixin(object):
    def bootstrap_storage(self):
        if not hasattr(self, "storage"):
            if hasattr(self, "bot") and hasattr(self.bot, "storage"):
                self.storage = self.bot.storage
            else:
                # The STORAGE_BACKEND setting points to a specific module namespace
                # redis => will.storage.redis_backend
                # couchbase => will.storage.couchbase_backend
                # etc...
                module_name = ''.join([
                    'will.storage.',
                    getattr(settings, 'STORAGE_BACKEND', 'redis'),
                    '_storage'
                ])
                storage_module = importlib.import_module(module_name)

                # Now create our storage object using the bootstrap function
                # from within the import
                self.storage = storage_module.bootstrap(settings)

    def save(self, key, value, expire=None):
        self.bootstrap_storage()
        try:
            return self.storage.save(key, pickle.dumps(value), expire=expire)
        except Exception:
            logging.exception("Unable to save %s", key)

    def clear(self, key):
        self.bootstrap_storage()
        try:
            return self.storage.clear(key)
        except Exception:
            logging.exception("Unable to clear %s", key)

    def clear_all_keys(self):
        self.bootstrap_storage()
        try:
            return self.storage.clear_all_keys()
        except Exception:
            logging.exception("Unable to clear all keys")

    def load(self, key, default=None):
        self.bootstrap_storage()
        try:
            val = self.storage.load(key)
            if val is not None:
                return pickle.loads(val)
            return default
        except Exception:
            logging.exception("Failed to load %s", key)

    def size(self):
        self.bootstrap_storage()
        try:
            return self.storage.size()
        except Exception:
            logging.exception("Failed to get the size of our storage")

    # list specific save/load/clear operations

    def pop(self, key, value):
        tmp_value = self.load(key)
        if tmp_value is None:
            pass
        else:
            tmp_value.remove(value)
            self.save(key, tmp_value)

    def append(self, key, value, expire=None):
        tmp_value = self.load(key)
        if tmp_value is None:
            self.save(key, [value], expire)
        else:
            tmp_value.append(value)
            self.save(key, tmp_value, expire)
