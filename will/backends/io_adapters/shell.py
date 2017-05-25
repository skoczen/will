import cmd
import random
import sys
import logging
from multiprocessing.queues import Empty
import requests
import threading
import readline
import traceback
from will.utils import Bunch, UNSURE_REPLIES
from .base import StdInOutIOBackend, Message

from will import settings


class ShellBackend(StdInOutIOBackend):
    friendly_name = "Interactive Shell"
    internal_name = "will.backends.io_adapters.shell"

    def send_direct_message(self, message_body, **kwargs):
        print("Will: %s" % message_body)

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        print("Will: %s" % message_body)

    def set_room_topic(self, room_id, topic):
        print("Will: Setting the Topic to %s" & topic)

    def handle_incoming_event(self, event):
        if event.type == "message":
            m = Message(
                content=event.content,
                type=event.type,
                is_direct=True,
                is_private_chat=True,
                is_group_chat=False,
                backend=self.name,
                sender=Bunch(nick="You"),
                will_is_mentioned=False,
                will_said_it=False,
                backend_supports_acl=False,
                source=Bunch()
            )

            self.input_queue.put(m)
        else:
            # An event type the shell has no idea how to handle.
            pass

    def handle_outgoing_event(self, event):
        # Print any replies.
        if event.type in ["say", "reply"]:
            self.send_direct_message(event.content)

        elif event.type == "no_response":
            if len(event.source_message.content) > 0:
                self.send_direct_message(random.choice(UNSURE_REPLIES))

        # Regardless of whether or not we had something to say,
        # give the user a new prompt.
        sys.stdout.write("You:  ")
        sys.stdout.flush()

    def bootstrap(self):
        # Do this to get the first "you" prompt.
        self.input_queue.put(Message(
                content="",
                type="chat",
                is_direct=True,
                is_private_chat=True,
                is_group_chat=False,
                backend=self.name,
                sender=Bunch(nick="You"),
                will_is_mentioned=False,
                will_said_it=False,
                backend_supports_acl=False,
            ))
