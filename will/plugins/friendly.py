import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class FriendlyPlugin(WillPlugin):

    @respond_to("^hi")
    def hi(self, message):
        """hi: I know how to say hello."""
        self.reply(message, "hello!")

    @hear("^(good )?(morning?)")
    def morning(self, message):
        self.say("mornin', %s" % message.sender.nick, message=message)

    @hear("^(good ?|g')?('?night)")
    def good_night(self, message):
        now = datetime.datetime.now()
        if now.weekday() == 4:  # Friday
            self.say("have a good weekend!", message=message)
        else:
            self.say("have a good night!", message=message)
