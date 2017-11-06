import datetime
import random
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

THANKS_REPLIES = [
    "Thank you!",
    "Aww, thanks!",
    ":)",
]


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

    @hear("happy birthday")
    def hear_happy_birthday(self, message):
        today = datetime.datetime.today()
        if today.month == 12 and (today.day == 4 or today.day == 5):
            self.reply(random.choice(THANKS_REPLIES))
