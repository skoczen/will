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


class ShellListener(cmd.Cmd, object):
    """Simple command processor example."""

    friendly_name = "Shell"
    prompt = " You: "

    def __init__(self, *args, **kwargs):
        if "bot" in kwargs:
            self.bot = kwargs["bot"]
            del kwargs["bot"]
        super(ShellListener, self).__init__(*args, **kwargs)

    def default(self, line):
        if line:
            # This is all pretty hacky to get a version working, and then
            # it'll be properly cleaned up and abstracted later.
            msg = Bunch(
                body=line,
                type="chat",
                mucnick="",
                sender=Bunch(hipchat_id="123", nick="You"),
            )
            # Reserved keyword joys.
            msg["from"] = "me"
            line = "%s\n" % line

            for l in self.bot.message_listeners:
                search_matches = l["regex"].search(line)
                if (
                        search_matches  # The search regex matches
                ):
                    try:
                        thread_args = [msg, ] + l["args"]

                        def fn(listener, args, kwargs):
                            try:
                                listener["fn"](*args, **kwargs)
                            except:
                                content = "I ran into trouble running %s.%s:\n\n%s" % (
                                    listener["class_name"],
                                    listener["function_name"],
                                    traceback.format_exc(),
                                )

                                if msg is None or msg["type"] == "groupchat":
                                    if msg.sender and "nick" in msg.sender:
                                        content = "@%s %s" % (msg.sender["nick"], content)
                                    self.bot.send_room_message(None, content, color="red")
                                elif msg['type'] in ('chat', 'normal'):
                                    self.bot.send_direct_message(None, content)

                        fn(l, thread_args, search_matches.groupdict())
                    except:
                        logging.critical(
                            "Error running %s.  \n\n%sContinuing...\n" % (
                                l["function_name"],
                                traceback.format_exc()
                            )
                        )

            # self.add_event_handler("roster_update", self.join_rooms)
            # self.add_event_handler("session_start", self.session_start)
            # self.add_event_handler("message", self.message_recieved)
            # self.add_event_handler("groupchat_message", self.room_message)

    def postloop(self):
        pass



class ShellBackend(IOBackend):
    use_stdin = True
    friendly_name = "Interactive Shell"

    def send_direct_message(self, user_id, message_body, html=False, notify=False, **kwargs):
        print("Will: %s" % message_body)
        # sys.stdout.flush()


    def send_direct_message_reply(self, message, message_body):
        print("Will: %s" % message_body)
        # sys.stdout.flush()


    def send_room_message(self, room_id, message_body, html=False, color="green", notify=False, **kwargs):
        print("Will: %s" % message_body)
        # sys.stdout.flush()


    def set_room_topic(self, room_id, topic):
        print("Will: Setting the Topic to %s" &  topic)
        # sys.stdout.flush()


    def get_user(self, user_id, q=None):
        return {}


    @property
    def get_user_list(self):
        return []


    def init_shell_client(self, bot=None):
        # self.shell_cmd = ShellListener(bot=bot)
        # return self.shell_cmd
        pass

    def event_handler_loop(self):
        while True:
            try:
                event = self.stdin_queue.get(timeout=0.4)
                # Pass this along to whereever it should go.
                # will.queues?
                if event["type"] == "message":
                    m = Message(
                        body=event["content"],
                        source=event["source"],
                        type=event["type"],
                        is_direct=True,
                        backend=self.name
                    )

                    self.input_queue.put(m)
                # IO Adapters are responsible for taking the input, 
                # adding their own metadata and standard info
                # and providing a return method

                # Standard info:
                # is_direct
                # message_body
                # medium/backend
                # timestamp
                # message_hash (for queues) (subclass?)

            except Empty:
                pass
            except:
                import traceback; traceback.print_exc();
                pass
            try:
                output_event = self.output_queue.get(timeout=0.1)
                # Pass this along to whereever it should go.
                # will.queues?
                if output_event["type"] in ["say", "reply"]:
                    print "Will: %s " % output_event["content"]

                # if output_event["type"] == "no_response":
                sys.stdout.write("You:  ")
                sys.stdout.flush()

            except Empty:
                pass
            except:
                import traceback; traceback.print_exc();
                pass


    def start(self, name, input_queue, output_queue, stdin_queue=None):
        if stdin_queue:
            self.stdin_queue = stdin_queue
        self.name = name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.init_shell_client()
        self.event_handler_loop()

        # self.shell_cmd.cmdloop("\n\n")

    