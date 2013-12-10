import datetime
import requests
from will.plugin_base import WillPlugin
from will.decorators import respond_to, periodic, one_time_task, hear, randomly, route, rendered_template
import will.settings as settings


class StoragePlugin(WillPlugin):

    @respond_to("^SERIOUSLY. Clear (?P<key>.*)", case_sensitive=True)
    def clear_storage(self, message, key=None):
        if not key:
            self.say("Sorry, you didn't say what to clear.", message=message)
        else:
            self.clear(key)
            self.say("Ok. Clearing the storage for %s" % key, message=message)

    @respond_to("^SERIOUSLY. REALLY. Clear all keys.", case_sensitive=True)
    def clear_all_keys_listener(self, message):
        self.say("Ok, I'm clearing them. You're probably going to want to restart me. I just forgot everything.", message=message)
        self.clear_all_keys()
        
