import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class PingPlugin(WillPlugin):

    @respond_to("^ping$")
    def ping(self, message):
        self.reply(message, "PONG")
