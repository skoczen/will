from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template


class HelpPlugin(WillPlugin):

    @respond_to("^help")
    def help(self, message):
        """help: the normal help you're reading."""
        # help_data = self.load("help_files")
        help_modules = self.load("help_modules")

        self.say("Sure thing, %s." % message.sender.nick, message=message)
        help_text = "Here's what I know how to do:"

        for k in sorted(help_modules, key=lambda x: x[0]):
            help_data = help_modules[k]
            if help_data and len(help_data) > 0:
                help_text += "<br/><br/><b>%s</b>:" % k
                for line in help_data:
                    if line:
                        if ":" in line:
                            line = "&nbsp; <b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
                        help_text += "<br/> %s" % line

        self.say(help_text, message=message, html=True)
