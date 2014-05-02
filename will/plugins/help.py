from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template


class HelpPlugin(WillPlugin):

    @respond_to("^help")
    def help(self, message):
        """help:  I like to help it, help it...I like to help it, help it...
I like to...MOVE IT!"""
        help_data = self.load("help_files")
        help_text = "Here is what I can do:"
        for line in help_data:
            if line:
                help_text += "\n{}".format(line.split('\n')[0])

        self.say(help_text, message=message)
