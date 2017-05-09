import logging
import re
import threading
import traceback

import settings
from utils import Bunch


class ListenerMixin(object):

    def hear_direct_message(self, message, io_metadata):
        # Add context, mark the backend, save the message to the broader conversation context and history.
        # Then, kick off the decision lifecycle.
        pass

    def hear_room_message(self, message, io_metadata):
        # Add context, mark the backend, save the message to the broader conversation context and history.
        # Then, kick off the decision lifecycle.
        pass
