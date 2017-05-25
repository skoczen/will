from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ItsLovePlugin(WillPlugin):

    @hear("i love(?: you,?)? will")
    def hear_love(self, message):
        self.say("I love you, too.", message=message)

    @respond_to("i love you")
    def hear_love_direct(self, message):
        self.say("I love you, too.", message=message)

    @hear("will is awesome")
    def hear_i_am_awesome(self, message):
        self.say("Aww, thanks!", message=message)

    @respond_to("you(?: are|'re)? (?:awesome|rock)")
    def hear_you_are_awesome(self, message):
        self.say("Takes one to know one, %s." % message.sender.first_name, message=message)
