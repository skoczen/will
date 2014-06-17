from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template
import re


class HelpPlugin(WillPlugin):

    @respond_to("^help on (?P<help_subject>.*)")
    def help_on(self, message, help_subject):
        all_regexes = self.load("all_listener_regexes")
        matches = ""
        for r in all_regexes:
            if re.search(help_subject, r):
                matches += "\n%s" % r
        if matches == "":
            help_text = "I don't know anything about that."
        else:
            help_text = "Here's what I know about that:%s" % matches
        self.say(help_text, message=message)

    @respond_to("^help$")
    def help(self, message):
        help_data = self.load("help_files")
        self.say("Sure thing, %s." % message.sender.nick, message=message)
        help_text = "Here's what I know how to do:"
        for plugin_name, plugin_cmds in help_data.iteritems():
            if filter(lambda x: x is not None, plugin_cmds):
                help_text += "<br/>%s" % plugin_name
            for line in plugin_cmds:
                if line:
                    if ":" in line:
                        line = "<b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
                    help_text += "<li>%s</li>" % line

        self.say(help_text, message=message, html=True)
