from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template
from will import settings

class HangoutPlugin(WillPlugin):

    @respond_to("^hangout")
    def hangout(self, message):
        self.say("Hangout: %s" % settings.WILL_HANGOUT_URL, message=message)
