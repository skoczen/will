import logging
import redis
from six.moves.urllib import parse
from .base import BasePubSub

SKIP_TYPES = ["psubscribe", "punsubscribe", ]


class RedisPubSub(BasePubSub):
    """
    A pubsub backend using Redis.

    You must supply a REDIS_URL setting that is passed through urlparse.

    Examples:

    * redis://localhost:6379/7
    * redis://rediscloud:asdfkjaslkdjflasdf@pub-redis-12345.us-east-1-1.2.ec2.garantiadata.com:12345
    """

    required_settings = [
        {
            "name": "REDIS_URL",
            "obtain_at": """You must supply a REDIS_URL setting that is passed through urlparse.

Examples:

* redis://localhost:6379/7
* redis://rediscloud:asdfkjaslkdjflasdf@pub-redis-12345.us-east-1-1.2.ec2.garantiadata.com:12345""",
        },
    ]

    def __init__(self, settings, *args, **kwargs):
        self.verify_settings(quiet=True)
        super(RedisPubSub, self).__init__(*args, **kwargs)
        url = parse.urlparse(settings.REDIS_URL)

        if hasattr(url, "path"):
            db = url.path[1:]
        else:
            db = 0
        max_connections = int(getattr(settings, 'REDIS_MAX_CONNECTIONS', None))
        connection_pool = redis.ConnectionPool(
            max_connections=max_connections, host=url.hostname,
            port=url.port, db=db, password=url.password
        )
        self.redis = redis.Redis(connection_pool=connection_pool)
        self._pubsub = self.redis.pubsub()

    def publish_to_backend(self, topic, body_str):
        logging.debug("publishing %s" % (topic,))
        return self.redis.publish(topic, body_str)

    def do_subscribe(self, topic):
        logging.debug("subscribed to %s" % topic)
        return self._pubsub.psubscribe(topic)

    def unsubscribe(self, topic):
        return self._pubsub.punsubscribe(topic)

    def get_from_backend(self):
        m = self._pubsub.get_message()
        if m and m["type"] not in SKIP_TYPES:
            return m
        return None


def bootstrap(settings):
    return RedisPubSub(settings)
