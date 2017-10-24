import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class MorninEveninPlugin(WillPlugin):

    @hear("^(good )?(morning?)")
    def morning(self, message):
        self.say("mornin', %s" % message.sender.handle, message=message)

    @hear("^(good ?|g')?('?night)")
    def good_night(self, message):
        now = datetime.datetime.now()
        if now.weekday() == 4:  # Friday
            self.say("have a good weekend!", message=message)
        else:
            self.say("have a good night!", message=message)
