
import logging
import traceback
import requests
import warnings

from will import settings
from will.decorators import require_settings
from .base import ExecutionBackend


class AllBackend(ExecutionBackend):

    def handle_execution(self, message):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                had_one_reply = False
                for m in message.generation_options:
                    self.execute(message, m)
                    had_one_reply = True

                if not had_one_reply:
                    self.no_response(message)

                return {}
            except:
                logging.critical(
                    "Error running %s.  \n\n%s\nContinuing...\n" % (
                        message.context.full_method_name,
                        traceback.format_exc()
                    )
                )
