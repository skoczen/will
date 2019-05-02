from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HelpPlugin(WillPlugin):

    @respond_to("help(?: (?P<plugin>.*))?$")
    def help(self, message, plugin=None):
        """help: the normal help you're reading."""
        # help_data = self.load("help_files")
        selected_modules = help_modules = self.load("help_modules")

        self.say("Sure thing, %s." % message.sender.first_name)

        help_text = "Here's what I know how to do:"
        if plugin and plugin in help_modules:
            help_text = "Here's what I know how to do about %s:" % plugin
            selected_modules = dict()
            selected_modules[plugin] = help_modules[plugin]

        for k in sorted(selected_modules, key=lambda x: x[0]):
            help_data = selected_modules[k]
            if help_data:
                help_text += "<br/><br/><b>%s</b>:" % k
                for line in help_data:
                    if line:
                        if ":" in line:
                            line = "&nbsp; <b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
                        help_text += "<br/> %s" % line

        self.say(help_text, html=True)
