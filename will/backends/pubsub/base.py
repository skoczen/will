import logging
import os
import redis
import traceback
from six.moves.urllib.parse import urlparse

from will.abstractions import Event
from will import settings
from will.mixins import SettingsMixin, EncryptionMixin

SKIP_TYPES = ["psubscribe", "punsubscribe", ]


class PubSubPrivateBase(SettingsMixin, EncryptionMixin):
    """
    The private bits of the base pubsub backend.
    """
    def __init__(self, *args, **kwargs):
        self.recent_hashes = []

    def publish(self, topic, obj, reference_message=None):
        """
        Sends an object out over the pubsub connection, properly formatted,
        and conforming to the protocol.  Handles pickling for the wire, etc.
        This method should *not* be subclassed.
        """
        logging.debug("Publishing topic (%s): \n%s" % (topic, obj))
        e = Event(
            data=obj,
            type=topic,
        )
        if hasattr(obj, "sender"):
            e.sender = obj.sender

        if reference_message:
            original_incoming_event_hash = None
            if hasattr(reference_message, "original_incoming_event_hash"):
                original_incoming_event_hash = reference_message.original_incoming_event_hash
            elif hasattr(reference_message, "source") and hasattr(reference_message.source, "hash"):
                original_incoming_event_hash = reference_message.source.hash
            elif hasattr(reference_message, "source") and hasattr(reference_message.source, "original_incoming_event_hash"):
                original_incoming_event_hash = reference_message.source.original_incoming_event_hash
            elif hasattr(reference_message, "hash"):
                original_incoming_event_hash = reference_message.hash
            if original_incoming_event_hash:
                e.original_incoming_event_hash = original_incoming_event_hash

        return self.publish_to_backend(
            self._localize_topic(topic),
            self.encrypt(e)
        )

    def unsubscribe(self, topic):
        # This is mostly here for semantic consistency.
        self.do_unsubscribe(topic)

    def _localize_topic(self, topic):
        cleaned_topic = topic
        if type(topic) == type([]):
            cleaned_topic = []
            for t in topic:
                if not t.startswith(settings.SECRET_KEY):
                    cleaned_topic.append("%s.%s" % (settings.SECRET_KEY, t))

        elif not topic.startswith(settings.SECRET_KEY):
            cleaned_topic = "%s.%s" % (settings.SECRET_KEY, topic)
        return cleaned_topic

    def subscribe(self, topic):
        return self.do_subscribe(self._localize_topic(topic))

    def get_message(self):
        """
        Gets the latest object from the backend, and handles unpickling
        and validation.
        """
        try:
            m = self.get_from_backend()
            if m and m["type"] not in SKIP_TYPES:
                return self.decrypt(m["data"])

        except AttributeError:
            raise Exception("Tried to call get message without having subscribed first!")
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error in watching pubsub get message: \n%s" % traceback.format_exc())
        return None


class BasePubSub(PubSubPrivateBase):
    """
    The base pubsub backend.
    Subclassing methods must implement:
    - do_subscribe()
    - unsubscribe()
    - publish_to_backend()
    - get_from_backend()
    """

    def do_subscribe(self, topic):
        """
        Registers with the backend to only get messages matching a specific topic.
        Where possible, wildcards are allowed
        """
        raise NotImplementedError

    def do_unsubscribe(self, topic):
        """Unregisters with the backend for a given topic."""
        raise NotImplementedError

    def publish_to_backend(self, topic, str):
        """Publishes a string to the backend with a given topic."""
        raise NotImplementedError

    def get_from_backend(self):
        """
        Gets the latest pending message from the backend (FIFO).
        Returns None if no messages are pending, and is expected *not* to be blocking.
        """
        raise NotImplementedError


def bootstrap(settings):
    return BasePubSub(settings)
