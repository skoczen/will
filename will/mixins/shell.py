import cmd
import sys
import logging
import requests
import threading
import readline
import traceback
from will.utils import Bunch

from will import settings

class ShellListener(cmd.Cmd, object):
    """Simple command processor example."""

    prompt = " You: "

    # def do_greet(self, person):
    #     """greet [person]
    #     Greet the named person"""
    #     if person:
    #         print "hi,", person
    #     else:
    #         print 'hi'

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



class ShellBackend(object):


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


    def init_shell_client(self, bot):
        self.shell_cmd = ShellListener(bot=bot)
        return self.shell_cmd


    def start_shell(self):
        self.shell_cmd.cmdloop("\n\n")
