from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ThanksPlugin(WillPlugin):

    @respond_to("^(?:thanks|thank you|tx|thx|ty|tyvm)")
    def respond_to_thanks(self, message):
        self.reply("You're welcome!")

    @hear("(thanks|thank you|tx|thx|ty|tyvm),? (will|william)")
    def hear_thanks(self, message):
        self.say("You're welcome!", message=message)
