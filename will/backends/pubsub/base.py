import dill as pickle
import redis
import urlparse
from will.abstractions import Event

SKIP_TYPES = ["psubscribe", "punsubscribe", ]


class BasePubSub(object):
    """
    The base pubsub backend.
    Subclassing methods must implement:
    - subscribe()
    - unsubscribe()
    - publish_to_backend()
    - get_from_backend()

    """

    def subscribe(self, topic):
        """
        Registers with the backend to only get messages matching a specific topic.
        Where possible, wildcards are allowed
        """

        raise NotImplementedError

    def unsubscribe(self, topic):
        """Unregisters with the backend for a given topic."""
        raise NotImplementedError

    def publish_to_backend(self, topic, str):
        """Publishes a string to the backend with a given topic."""
        raise NotImplementedError

    def get_from_backend(self):
        """
        Gets the latest pending message from the backend (FIFO).
        Returns None if no messages are pending.
        """
        raise NotImplementedError

    def publish(self, topic, obj, reference_message=None):
        """
        Sends an object out over the pubsub connection, properly formatted,
        and conforming to the protocol.  Handles pickling for the wire, etc.
        This method should *not* be subclassed.
        """
        print "-> publishing to %s" % topic
        print obj
        e = Event(
            data=obj,
            type=topic,
        )
        if reference_message:
            source_hash = None
            if hasattr(reference_message, "source_hash"):
                source_hash = reference_message.source_hash
            elif hasattr(reference_message, "source") and hasattr(reference_message.source, "hash"):
                source_hash = reference_message.source.hash
            elif hasattr(reference_message, "source") and hasattr(reference_message.source, "source_hash"):
                source_hash = reference_message.source.source_hash
            elif hasattr(reference_message, "hash"):
                source_hash = reference_message.hash
            if source_hash:
                e.source_hash = source_hash

        msg = pickle.dumps(e)
        return self.publish_to_backend(topic, msg)

    def get_message(self):
        """
        Gets the latest object from the backend, and handles unpickling
        and validation.
        """
        try:
            m = self.get_from_backend()
            if m and m["type"] not in SKIP_TYPES:
                loaded_message = pickle.loads(m["data"])
                return loaded_message
        except AttributeError:
            raise Exception("Tried to call get message without having subscribed first!")
        except:
            import traceback; traceback.print_exc();
        return None


def bootstrap(settings):
    return RedisPubSub(settings)
