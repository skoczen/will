import logging
import traceback
import zmq
from .base import BasePubSub

SKIP_TYPES = ["psubscribe", "punsubscribe", ]

DIVIDER = "|WILL-SPLIT|"


class ZeroMQPubSub(BasePubSub):
    """
    A pubsub backend using ZeroMQ.

    You must supply a ZEROMQ_URL setting that is passed directly to zmq.connect()

    Examples:

    * zeromq://localhost:63797
    * zeromq://ZeroMQ:asdfkjaslkdjflasdf@pub-zeromq-12345.us-east-1-1.2.ec2.zeromq.com:12345
    """

    required_settings = [
        {
            "name": "ZEROMQ_URL",
            "obtain_at": """You must supply a ZEROMQ_URL setting that is passed through urlparse.

Examples:

* zeromq://localhost:63797
* zeromq://ZeroMQ:asdfkjaslkdjflasdf@pub-zeromq-12345.us-east-1-1.2.ec2.zeromq.com:12345""",
        },
    ]

    def __init__(self, settings, *args, **kwargs):
        self.verify_settings(quiet=True)
        logging.error(
            "The ZeroMQ Backend isn't ready for prime-time yet. Please "
            "test closely, and report any problems at Will's github page!"
        )
        super(ZeroMQPubSub, self).__init__(*args, **kwargs)
        context = zmq.Context.instance()
        self.pub_socket = context.socket(zmq.PUB)
        try:
            self.pub_socket.bind(settings.ZEROMQ_URL)
        except:
            self.pub_socket.connect(settings.ZEROMQ_URL)

        sub_context = zmq.Context.instance()
        self.sub_socket = sub_context.socket(zmq.SUB)

        self.sub_socket.connect(settings.ZEROMQ_URL)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')

        # self.poller = zmq.Poller()
        # self.poller.register(self.sub_socket, zmq.POLLIN)

    def publish_to_backend(self, topic, body_str):
        return self.pub_socket.send("%s%s%s" % (topic, DIVIDER, body_str))

    def do_subscribe(self, topic):
        if type(topic) == type([]):
            for t in topic:
                self.sub_socket.setsockopt(zmq.SUBSCRIBE, t)
        else:
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

    def unsubscribe(self, topic):
        if type(topic) == type([]):
            for t in topic:
                self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, t)
        else:
            self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def get_from_backend(self):
        try:
            s = self.sub_socket.recv(zmq.DONTWAIT)
            if s:
                topic, m = s.split(DIVIDER)
                if m and m["type"] not in SKIP_TYPES:
                    return m
        except zmq.Again:
            return None

        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical(
                "Error getting message from ZeroMQ backend: \n%s" % traceback.format_exc()
            )
        return None


def bootstrap(settings):
    return ZeroMQPubSub(settings)
