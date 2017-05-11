import cmd
import sys
import logging
from multiprocessing.queues import Empty
import requests
import threading
import readline
import traceback
from will.utils import Bunch
from .base import IOBackend, Message

from will import settings


class ShellBackend(IOBackend):
    use_stdin = True
    friendly_name = "Interactive Shell"

    def send_direct_message(self, message_body, **kwargs):
        print("Will: %s" % message_body)
        # sys.stdout.flush()

    def send_direct_message_reply(self, message, message_body):
        print("Will: %s" % message_body)
        # sys.stdout.flush()

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        print("Will: %s" % message_body)
        # sys.stdout.flush()

    def set_room_topic(self, room_id, topic):
        print("Will: Setting the Topic to %s" & topic)
        # sys.stdout.flush()

    def get_user(self, user_id, q=None):
        return {}

    @property
    def get_user_list(self):
        return []

    def event_handler_loop(self):
        while True:
            try:
                # Input queue
                event = self.stdin_queue.get(timeout=0.4)

                if event["type"] == "message":
                    m = Message(
                        body=event["content"],
                        source=event["source"],
                        type=event["type"],
                        is_direct=True,
                        backend=self.name
                    )

                    self.input_queue.put(m)
                else:
                    # An event type the shell has no idea how to handle.
                    pass
            except Empty:
                # No input
                pass
            except (KeyboardInterrupt, SystemExit):
                pass

            # Output Queue
            try:
                output_event = self.output_queue.get(timeout=0.1)

                # Print any replies.
                if output_event["type"] in ["say", "reply"]:
                    self.send_direct_message(output_event["content"])

                # Regardless of whether or not we had something to say,
                # give the user a new prompt.
                sys.stdout.write("You:  ")
                sys.stdout.flush()

            except Empty:
                pass
            except (KeyboardInterrupt, SystemExit):
                pass

    def start(self, name, input_queue, output_queue, stdin_queue=None):
        if stdin_queue:
            self.stdin_queue = stdin_queue
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.event_handler_loop()
