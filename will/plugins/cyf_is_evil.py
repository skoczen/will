import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class CYFIsEvilPlugin(WillPlugin):

    @respond_to("\(cyf\)")
    def scream_from_cyf(self, message):
        self.say("NOOOOOOOooooooOOOOOO!!!  It huurts!!")
