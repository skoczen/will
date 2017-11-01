import datetime
import random
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

RESPONSES = [
    "Pretty good, all things considered. You?",
    "Doing alright.  How are you?",
    "Pretty solid for a %(day_name)s, thanks.  And you?",
    "Last night was crazy, but today is looking good. What about you?",
    "A little bored, if I'm honest.  How're you?",
    "Up and down, but good overall.  What about you?",
]


class HowAreYouPlugin(WillPlugin):

    @hear("^how are you\?")
    def how_are_you(self, message):
        now = datetime.datetime.now()
        context = {
            "day_name": now.strftime("%A")
        }
        reply = random.choice(RESPONSES) % context
        message.said_to_how_are_you = True
        self.say(reply, message=message)

    # @hear("")
    # def how_are_you_reply(self, message):
    #     print(message.analysis["history"][0].data)
    #     print(message.analysis["history"][1].data)
