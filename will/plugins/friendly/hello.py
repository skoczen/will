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
