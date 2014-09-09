from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HelloPlugin(WillPlugin):

    @respond_to("^hi$", allowed_typos=0)
    def hi(self, message):
        """hi: I know how to say hello!"""
        self.reply(message, "hello!")

    @respond_to("^hello$", allowed_typos=1.3)
    def hello(self, message):
        self.reply(message, "hi!")
