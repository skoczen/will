from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings


class HangoutPlugin(WillPlugin):

    @require_settings("HANGOUT_URL",)
    @respond_to("^hangout")
    def hangout(self, message):
        self.say("Hangout: %s" % settings.HANGOUT_URL, message=message)
