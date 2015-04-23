import logging
import redis
import traceback
import urlparse
import dill as pickle
from will import settings
from will.utils import show_valid, error, warn, note


class StorageMixin(object):
    def bootstrap_storage(self):
        if not hasattr(self, "storage"):
            if hasattr(self, "bot") and hasattr(self.bot, "storage"):
                self.storage = self.bot.storage
            else:
                # redis://localhost:6379/7
                # or
                # redis://rediscloud:asdfkjaslkdjflasdf@pub-redis-12345.us-east-1-1.2.ec2.garantiadata.com:12345
                url = urlparse.urlparse(settings.REDIS_URL)

                if hasattr(url, "path"):
                    db = url.path[1:]
                else:
                    db = 0
                max_connections = getattr(settings, 'REDIS_MAX_CONNECTIONS',
                                          None)
                connection_pool = redis.ConnectionPool(
                    max_connections=max_connections, host=url.hostname,
                    port=url.port, db=db, password=url.password
                )
                self.storage = redis.Redis(connection_pool=connection_pool)

    def save(self, key, value, expire=0):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()

        try:
            if expire:
                ret = self.storage.setex(key, pickle.dumps(value), expire)
            else:
                ret = self.storage.set(key, pickle.dumps(value))

            return ret
        except:
            logging.critical("Unable to save %s: \n%s" %
                             (key, traceback.format_exc()))

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
