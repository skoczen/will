import importlib
import logging
import dill as pickle
import functools
from will import settings


class PubSubMixin(object):
    def bootstrap_pubsub(self):
        if not hasattr(self, "pubsub"):
            if hasattr(self, "bot") and hasattr(self.bot, "pubsub"):
                self.pubsub = self.bot.pubsub
            else:
                # The PUBSUB_BACKEND setting points to a specific module namespace
                # redis => will.pubsub.redis_backend
                # zeromq => will.pubsub.zeromq_backend
                # etc...
                module_name = ''.join([
                    'will.backends.pubsub.',
                    getattr(settings, 'PUBSUB_BACKEND', 'redis'),
                    '_pubsub'
                ])
                pubsub_module = importlib.import_module(module_name)

                # Now create our pubsub object using the bootstrap function
                # from within the import
                self.pubsub = pubsub_module.bootstrap(settings)

    def subscribe(self, topic):
        self.bootstrap_pubsub()
        try:
            return self.pubsub.subscribe(topic)
        except Exception:
            logging.exception("Unable to subscribe to %s", topic)

    def publish(self, topic, obj):
        self.bootstrap_pubsub()
        try:
            return self.pubsub.publish(topic, obj)
        except Exception:
            logging.exception("Unable to publish %s to %s", (obj, topic))

    def unsubscribe(self, topic):
        self.bootstrap_pubsub()
        try:
            return self.pubsub.unsubscribe(topic)
        except Exception:
            logging.exception("Unable to unsubscribe to %s", topic)
