import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template

# This doesn't work because dill can't pickle self.
# Very unlikely, but possible this will fix it:
# https://github.com/uqfoundation/dill/issues/9
def test_fn(bot, msg):
    print "foo"
    # bot.say("ran.", message=msg)


class FriendlyPlugin(WillPlugin):

    @respond_to("^hi")
    def hi(self, message):
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


    @respond_to("^test")
    def good_night(self, message):


        now = datetime.datetime.now()
        when = datetime.timedelta(seconds=10) + now
        self.schedule(when, test_fn, self, message)