from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class HelpPlugin(WillPlugin):

    @respond_to("^help")
    def help(self, message):
        all_regexes = self.load("all_listener_regexes")
        help_text = "Here's everything I know how to listen to:"
        for r in all_regexes:
            help_text += "\n%s" % r

        self.say(help_text, message=message)
