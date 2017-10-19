import imp
import logging
import traceback
import requests
import warnings

from will import settings
from will.decorators import require_settings
from will.utils import Bunch
from .base import ExecutionBackend


class BestScoreBackend(ExecutionBackend):

    def _publish_fingerprint(self, option, message):
        return "%s - %s" % (option.context.plugin_info["full_module_name"], option.context.full_method_name)

    def handle_execution(self, message):
        published_list = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                had_one_reply = False
                logging.info("message.generation_options")
                logging.info(message.generation_options)
                top_score = -1
                for m in message.generation_options:
                    logging.debug(m)
                    if m.score > top_score:
                        top_score = m.score
                logging.debug("top_score")
                logging.debug(top_score)
                for m in message.generation_options:
                    if m.score >= top_score:
                        s = self._publish_fingerprint(m, message)
                        if not s in published_list:
                            published_list.append(s)
                            self.execute(message, m)
                            had_one_reply = True

                if not had_one_reply:
                    self.no_response(message)

                return {}
            except:
                logging.critical(
                    "Error running %s.  \n\n%s\nContinuing...\n" % (
                        message,
                        traceback.format_exc()
                    )
                )
