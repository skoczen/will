import logging
from multiprocessing import Process
import traceback
import sys
import zmq
from .base import BasePubSub
from will.mixins import PubSubMixin, SleepMixin

SKIP_TYPES = ["psubscribe", "punsubscribe", ]

DIVIDER = "|WILL-SPLIT|"


class ZeroMQPubSub(BasePubSub, SleepMixin):
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
        logging.warning(
            "The ZeroMQ Backend isn't ready for prime-time yet. Please "
            "test closely, and report any problems at Will's github page!"
        )
        super(ZeroMQPubSub, self).__init__(*args, **kwargs)

        sub_context = zmq.Context()
        self.sub_socket = sub_context.socket(zmq.SUB)

        self.sub_socket.connect(settings.ZEROMQ_URL)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '',)
        print self.sub_socket
        try:
            # print self.sub_socket.recv(flags=zmq.NOBLOCK)
            self.get_from_backend()
        except zmq.Again:
            print "Again"
        print "read once"

        context = zmq.Context()
        self.pub_socket = context.socket(zmq.PUB)
        self.pub_socket.setsockopt(zmq.LINGER, 500)
        try:
            self.pub_socket.bind(settings.ZEROMQ_URL)
            print "bind"
        except:
            self.pub_socket.connect(settings.ZEROMQ_URL)
            print "connect"

        # self.poller = zmq.Poller()
        # self.poller.register(self.sub_socket, zmq.POLLIN)

    def publish_to_backend(self, topic, body_str):
        print "publish_to_backend: %s" % topic
        print "%s%s%s" % (topic, DIVIDER, body_str)
        return self.pub_socket.send("%s%s%s" % (topic, DIVIDER, body_str), flags=zmq.NOBLOCK)

    def do_subscribe(self, topic):
        print "subscribe: %s" % topic
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
            print "get_from_backend"
            msg = self.sub_socket.recv(flags=zmq.NOBLOCK)
            print "past recv"
            if msg:
                # print "topic: %s " % topic
                print "msg: %s " % msg
                return msg
            else:
                print "nonblock return"
            return None
            # s = self.sub_socket.recv()
            # print "found"
            # print s
            # if s:
            #     topic, m = s.split(DIVIDER)
            #     if m and m["type"] not in SKIP_TYPES:
            #         return m

        except zmq.Again:
            print "again"
            return None

        except (KeyboardInterrupt, SystemExit):
            sys.exit(1)
        except:
            logging.critical(
                "Error getting message from ZeroMQ backend: \n%s" % traceback.format_exc()
            )
        return None


def bootstrap(settings):
    def bootstrap_zeromq_thread():
        return ZeroMQPubSub(settings)

    zeromq_thread = Process(target=bootstrap_zeromq_thread)
    return ZeroMQPubSub(settings)
