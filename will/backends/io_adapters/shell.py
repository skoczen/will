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
from .base import StdInOutIOBackend, Message, Person, Channel

from will import settings


class ShellBackend(StdInOutIOBackend):
    friendly_name = "Interactive Shell"
    internal_name = "will.backends.io_adapters.shell"
    partner = Person(
        id="you",
        handle="you",
        source=Bunch(),
        name="Friend",
    )

    def send_direct_message(self, message_body, **kwargs):
        print("Will: %s" % message_body)

    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        print("Will: %s" % message_body)

    def set_room_topic(self, room_id, topic):
        print("Will: Setting the Topic to %s" & topic)

    def handle_incoming_event(self, event):
        if event.type == "message":
            m = Message(
                content=event.content.strip(),
                type=event.type,
                is_direct=True,
                is_private_chat=True,
                is_group_chat=False,
                backend=self.name,
                sender=self.partner,
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
        # Bootstrap must provide a way to to have:
        # a) self.handle_incoming_event fired, or incoming events put into self.incoming_queue
        # b) any necessary threads running for a)
        # c) self.me (Person) defined, with Will's info
        # d) self.people (dict of People) defined, with everyone in an organization/backend
        # e) self.channels (dict of Channels) defined, with all available channels/rooms.
        #    Note that Channel asks for members, a list of People.
        # f) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
        #    with a maximum lag of 60 seconds.
        self.people = {}
        self.channels = {}
        self.me = Person(
            id="will",
            handle="will",
            source=Bunch(),
            name="William T. Botterton",
        )

        # Do this to get the first "you" prompt.
        self.input_queue.put(Message(
                content="",
                type="chat",
                is_direct=True,
                is_private_chat=True,
                is_group_chat=False,
                backend=self.internal_name,
                sender=self.partner,
                will_is_mentioned=False,
                will_said_it=False,
                backend_supports_acl=False,
            ))
