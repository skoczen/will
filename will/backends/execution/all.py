import imp
import logging
import traceback
import requests
import warnings

from will import settings
from will.decorators import require_settings
from will.plugin import Event
from .base import ExecutionBackend


class AllBackend(ExecutionBackend):

    def handle_execution(self, message):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                had_one_reply = False
                for m in message.generation_options:
                    logging.info("handle_execution")
                    logging.info(m)
                    logging.info(m.__dict__)
                    logging.info(m.context)
                    logging.info(m.context.full_method_name)
                    logging.info(self.bot)
                    logging.info(self.bot.pubsub)

                    # Question: do we need to do this via self.bot, or can we re-instantiate
                    # the execution thread (and in the process, magically provide/handle self.message)?
                    module = imp.load_source(m.context.plugin_info["parent_name"], m.context.plugin_info["parent_path"])
                    logging.info("module")
                    logging.info(module)
                    cls = getattr(module, m.context.plugin_info["name"])
                    # Do we need self.bot?
                    instantiated_module = cls(message=message, bot=self.bot)
                    logging.info("instantiated_module")
                    logging.info(instantiated_module)
                    method = getattr(instantiated_module, m.context.function_name)

                    # live_listener = self.bot.message_listeners[m.context.full_method_name]
                    thread_args = [message, ] + m.context["args"]

                    self.execute(
                        method,
                        *thread_args,
                        **m.context.search_matches
                    )
                    logging.info("Executed")
                    had_one_reply = True
                if not had_one_reply:
                    self.bot.pubsub.publish("message.no_response", {'source': message}, reference_message=message)

                return {}
            except:
                logging.critical(
                    "Error running %s.  \n\n%s\nContinuing...\n" % (
                        m.context.full_method_name,
                        traceback.format_exc()
                    )
                )
