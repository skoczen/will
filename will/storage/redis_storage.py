import redis
from six.moves.urllib import parse


class RedisStorage(object):
    """
    A storage backend using Redis.

    You must supply a REDIS_URL setting that is passed through urlparse.

    Examples:

    * redis://localhost:6379/7
    * redis://rediscloud:asdfkjaslkdjflasdf@pub-redis-12345.us-east-1-1.2.ec2.garantiadata.com:12345
    """
    def __init__(self, settings):
        url = parse.urlparse(settings.REDIS_URL)

        if hasattr(url, "path"):
            db = url.path[1:]
        else:
            db = 0
        max_connections = getattr(settings, 'REDIS_MAX_CONNECTIONS', None)
        connection_pool = redis.ConnectionPool(
            max_connections=max_connections, host=url.hostname,
            port=url.port, db=db, password=url.password
        )
        self.redis = redis.Redis(connection_pool=connection_pool)

    def save(self, key, value, expire=None):
        return self.redis.set(key, value, ex=expire)

    def clear(self, key):
        return self.redis.delete(key)

    def clear_all_keys(self):
        return self.redis.flushdb()

    def load(self, key):
        return self.redis.get(key)

    def size(self):
        return self.redis.info()["used_memory_human"]


def bootstrap(settings):
    return RedisStorage(settings)
