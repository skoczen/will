import binascii
import base64
import codecs
import dill as pickle
import hashlib
import logging
import os
import redis
import traceback
import urlparse
from Crypto.Cipher import AES
import random
from will.abstractions import Event
from will import settings
from will.mixins import SettingsMixin

SKIP_TYPES = ["psubscribe", "punsubscribe", ]

if settings.ENABLE_INTERNAL_ENCRYPTION:
    BS = 16
    key = hashlib.sha256(settings.SECRET_KEY).digest()


def pad(s):
    s = s + (BS - len(s) % BS) * "~"
    return s


def unpad(s):
    while s.endswith("~"):
        s = s[:-1]
    return s


def pack_for_wire(raw):
    try:
        enc = binascii.b2a_base64(pickle.dumps(raw, -1))
        if settings.ENABLE_INTERNAL_ENCRYPTION:
            iv = binascii.b2a_hex(os.urandom(8))
            cipher = AES.new(key, AES.MODE_CBC, iv)
            enc = binascii.b2a_base64(cipher.encrypt(pad(enc)))
            return "%s/%s" % (iv, enc)
        else:
            return enc
    except:
        logging.critical("Error preparing message for the wire: \n%s" % traceback.format_exc())
        return None


def unpack_from_wire(enc):
    try:
        if settings.ENABLE_INTERNAL_ENCRYPTION:
            iv = enc[:BS]
            enc = enc[BS+1:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            enc = unpad(cipher.decrypt(binascii.a2b_base64(enc)))
        obj = pickle.loads(binascii.a2b_base64(enc))
        return obj
    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        logging.critical("Error unpacking message from the wire: \n%s" % traceback.format_exc())
        return None


class BasePubSub(SettingsMixin):
    """
    The base pubsub backend.
    Subclassing methods must implement:
    - subscribe()
    - unsubscribe()
    - publish_to_backend()
    - get_from_backend()

    """
    def __init__(self, *args, **kwargs):
        self.recent_hashes = []

    def do_subscribe(self, topic):
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
        logging.debug("Publishing topic (%s): \n%s" % (topic, obj))
        e = Event(
            data=obj,
            type=topic,
        )
        # TODO: Decide on this.  It's hacky, but it makes backwards
        # compatability easier.
        if hasattr(obj, "sender"):
            e.sender = obj.sender

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

        return self.publish_to_backend(
            self._localize_topic(topic),
            pack_for_wire(e)
        )

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
                loaded_message = unpack_from_wire(m["data"])
                # Handling inconsistent backends, but appears to no longer be an issue.
                # if not loaded_message["hash"] in self.recent_hashes:
                #     self.recent_hashes.append(loaded_message["hash"])
                #     if len(self.recent_hashes) > 100:
                #         self.recent_hashes = self.recent_hashes[1:]
                return loaded_message
                # print(loaded_message)
                # loaded_message = pickle.loads(
                #     dec
                # )
        except AttributeError:
            raise Exception("Tried to call get message without having subscribed first!")
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error in watching pubsub get message: \n%s" % traceback.format_exc())
        return None


def bootstrap(settings):
    return BasePubSub(settings)
