import imp
import logging
import signal
import traceback
from will import settings
from will.decorators import require_settings
from will.acl import test_acl
from will.abstractions import Event
from multiprocessing import Process


class ExecutionBackend(object):
    is_will_execution_backend = True

    def handle_execution(self, message, context):
        raise NotImplemented

    def no_response(self, message):
        self.bot.pubsub.publish(
            "message.no_response",
            message.data,
            reference_message=message.data.original_incoming_event
        )

    def not_allowed(self, message, explanation):

        self.bot.pubsub.publish(
            "message.outgoing.%s" % message.data.backend,
            Event(
                type="reply",
                content=explanation,
                source_message=message,
            ),
            reference_message=message.data.original_incoming_event
        )

    def execute(self, message, option):
        if "acl" in option.context:
            acl = option.context["acl"]
            if type(acl) == type("test"):
                acl = [acl]

            allowed = True
            if len(acl) > 0:
                allowed = test_acl(message, acl)

            if not allowed:
                acl_list = ""
                more_than_one_s = ""
                if len(acl) > 1:
                    more_than_one_s = "s"
                for i in range(0, len(acl)):
                    if i == 0:
                        acl_list = "%s" % acl[i]
                    elif i == len(acl) - 1:
                        acl_list = "%s or %s" % (acl_list, acl[i])
                    else:
                        acl_list = "%s, %s" % (acl_list, acl[i])
                explanation = "Sorry, but I don't have you listed in the %s group%s, which is required to do what you asked." % (acl_list, more_than_one_s)

                self.not_allowed(
                    message,
                    explanation
                )
                return

        if "say_content" in option.context:
            # We're coming from a generation engine like a chatterbot, which doesn't *do* things.
            self.bot.pubsub.publish(
                "message.outgoing.%s" % message.data.backend,
                Event(
                    type="reply",
                    content=option.context["say_content"],
                    source_message=message,
                ),
                reference_message=message.data.original_incoming_event
            )
        else:
            module = imp.load_source(option.context.plugin_info["parent_name"], option.context.plugin_info["parent_path"])
            cls = getattr(module, option.context.plugin_info["name"])

            instantiated_module = cls(message=message)
            method = getattr(instantiated_module, option.context.function_name)

            thread_args = [message, ] + option.context["args"]

            self.run_execute(
                method,
                *thread_args,
                **option.context.search_matches
            )

    def run_execute(self, target, *args, **kwargs):
        try:
            t = Process(
                target=target,
                args=args,
                kwargs=kwargs,
            )
            self.bot.running_execution_threads.append(t)
            t.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error running %s: \n%s" % (target, traceback.format_exc()))

    def __init__(self, bot=None, *args, **kwargs):
        self.bot = bot
        if not bot:
            raise Exception("Can't proceed without an instance of bot passed to the backend.")
        super(ExecutionBackend, self).__init__(*args, **kwargs)
