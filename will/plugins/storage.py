import datetime
import requests
from will.plugin_base import WillPlugin
from will.decorators import respond_to, scheduled, one_time_task, hear, randomly, crontab, route, rendered_template
import will.settings as settings


class StoragePlugin(WillPlugin):

    @respond_to("^SERIOUSLY. Clear (?P<key>.*)", case_sensitive=True)
    def clear_storage(self, message, key=None):
        if not key:
            self.say(message, "Sorry, you didn't say what to clear.")
        else:
            self.clear(key)
            self.say(message, "Ok. Clearing the storage for %s" % key)
