import imp
import logging
import traceback
import requests
import warnings

from will import settings
from will.decorators import require_settings
from will.plugin import Event
from will.utils import Bunch
from .base import ExecutionBackend


class BestScoreBackend(ExecutionBackend):

    def do_execute(self, message, option):
        logging.info("handle_execution")
        logging.info(option)
        logging.info(option.__dict__)
        logging.info(option.context)
        logging.info(option.context.full_method_name)
        logging.info(self.bot)
        logging.info(self.bot.pubsub)

        # Question: do we need to do this via self.bot, or can we re-instantiate
        # the execution thread (and in the process, magically provide/handle self.message)?
        module = imp.load_source(option.context.plugin_info["parent_name"], option.context.plugin_info["parent_path"])
        logging.info("module")
        logging.info(module)
        cls = getattr(module, option.context.plugin_info["name"])
        # Do we need self.bot?
        instantiated_module = cls(message=message, bot=self.bot)
        logging.info("instantiated_module")
        logging.info(instantiated_module)
        method = getattr(instantiated_module, option.context.function_name)

        # live_listener = self.bot.message_listeners[option.context.full_method_name]
        thread_args = [message, ] + option.context["args"]

        self.execute(
            method,
            *thread_args,
            **option.context.search_matches
        )
        logging.info("Executed")

    def handle_execution(self, message):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                had_one_reply = False
                logging.debug("message.generation_options")
                logging.debug(message.generation_options)
                top_score = -1
                for m in message.generation_options:
                    logging.debug(m)
                    if m.score > top_score:
                        top_score = m.score
                logging.debug("top_score")
                logging.debug(top_score)
                for m in message.generation_options:
                    if m.score >= top_score:
                        self.do_execute(message, m)

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
