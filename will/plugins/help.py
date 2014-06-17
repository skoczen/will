from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template
import re


class HelpPlugin(WillPlugin):

    @respond_to("^help on (?P<help_subject>.*)")
    def help_on(self, message, help_term):
        help(message, help_term)

    @respond_to("^help$")
    def help(self, message, help_term=None):
        help_data = self.load("help_files")
        help_text = ""
        for plugin_name, plugin_cmds in help_data.iteritems():
            help_text += "<br/>%s" % plugin_name
            for cmd in plugin_cmds:
                invocation = cmd["regex"]
                if "invocation" in cmd:
                    invocation = cmd["invocation"]
                action = cmd["name"]
                if "action" in cmd:
                    action = cmd["action"]
                help_text += "<li>%s: %s</li>" % (invocation, action)
        self.say(help_text, message=message, html=True)

