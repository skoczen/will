from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class StoragePlugin(WillPlugin):

    @respond_to("^How big is the db?", acl=["admins"])
    def db_size(self, message):
        self.bootstrap_storage()
        self.say("It's %s." % self.storage.size(), message=message)

    @respond_to("^SERIOUSLY. Clear (?P<key>.*)", case_sensitive=True, acl=["admins"])
    def clear_storage(self, message, key=None):
        if not key:
            self.say("Sorry, you didn't say what to clear.", message=message)
        else:
            self.say("Ok. Clearing the storage for %s" % key, message=message)
            res = self.clear(key)
            if res not in (None, True, False):
                self.say("Something happened while clearing: %s" % res, message=message)

    @respond_to("^SERIOUSLY. REALLY. Clear all keys.$", case_sensitive=True, acl=["admins"])
    def clear_all_keys_listener(self, message):
        self.say(
            "Ok, I'm clearing them. You're probably going to want to restart me."
            "I just forgot everything, including who I am and where the chat room is.", message=message
        )
        res = self.clear_all_keys()
        if res not in (None, True, False):
            self.say("Something happened while clearing all keys: %s" % res, message=message)

    @respond_to("^Show (?:me )?(?:the )?storage for (?P<key>.*)", acl=["admins"])
    def show_storage(self, message, key=None):
        if not key:
            self.say("Not sure what you're looking for.", message=message)
        else:
            val = self.load(key)
            self.say("%s is %s" % (key, val), message=message)
