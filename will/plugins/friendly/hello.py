from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HelloPlugin(WillPlugin):

    @respond_to("^(?:hi|hey)$")
    def hi(self, message):
        """hi: I know how to say hello!"""
        self.reply("hello!")

    @respond_to("^hello$")
    def hello(self, message):
        self.reply("hi!")

    @periodic(hour='10', minute='05', day=4, month=12)
    def birthday(self, message):
        self.reply("Hey, so I didn't want to make a big deal of it, but today's my birthday!")

    @periodic(hour='12', minute='30', day_of_week='mon,tue,wed,thu,fri')
    def standup(self):
        self.say("Daily test of bug #295", room='alpha', notify=True)

    @periodic(minute='30', day_of_week='mon,tue,wed,thu,fri')
    def standup_hourly_test(self):
        self.say("Daily test of bug #295", room='alpha')

    @periodic(hour='12', minute='30', day_of_week='mon,tue,wed,thu,fri')
    def standup_hipchat(self):
        self.say("Test of bug #295", room='will and i', notify=True, service="hipchat")

    @periodic(minute='30', day_of_week='mon,tue,wed,thu,fri')
    def standup_hourly_test_hipchat(self):
        self.say("Hourly test of bug #295", room='will and i', service="hipchat")
