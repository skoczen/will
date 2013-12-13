import logging
import redis
import urlparse
import pickle
import dill as pickle
from dill.detect import errors
from will import settings


class StorageMixin(object):
    def bootstrap_storage(self):
        if hasattr(self, "bot"):
            self.storage = self.bot.storage
        elif not hasattr(self, "storage"):
            # redis://localhost:6379/7
            # or
            # redis://rediscloud:asdfkjaslkdjflasdf@pub-redis-12345.us-east-1-1.2.ec2.garantiadata.com:12345
            url = urlparse.urlparse(settings.WILL_REDIS_URL)

            if hasattr(url, "path"):
                db = url.path[1:]
            else:
                db = 0

            self.storage = redis.Redis(host=url.hostname, port=url.port, db=db, password=url.password)

    def save(self, key, value):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()

        try:
            return self.storage.set(key, pickle.dumps(value))
        except:
            logging.critical("Unable to save %s" % key)
            import traceback; traceback.print_exc();

    def clear(self, key):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()
        return self.storage.delete(key)

    def clear_all_keys(self):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()
        return self.storage.flushdb()

    def load(self, key, default=None):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()

        try:
            val = self.storage.get(key)
            if val is not None:
                return pickle.loads(val)
                
        except:
            logging.warn("Unable to load %s" % key)

        return default
