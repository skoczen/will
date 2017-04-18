from will.plugin import WillPlugin
from will.decorators import respond_to

import re


class HelpPlugin(WillPlugin):

    @staticmethod
    def append_module_to_reply(help_text, k, line):
        if ":" in line:
            if "<br/><br/><b>%s</b>:" % k not in help_text:
                help_text += "<br/><br/><b>%s</b>:" % k
            line = "&nbsp; <b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
        help_text += "<br/> %s" % line
        return help_text

    def collect_help_modules(self, help_text, pattern=None):
        help_modules = self.load("help_modules")
        for k in sorted(help_modules, key=lambda x: x[0]):
            help_data = help_modules[k]
            if help_data and len(help_data) > 0:
                for line in help_data:
                    if not pattern:
                        help_text = self.append_module_to_reply(help_text, k, line)
                    else:
                        if re.search(r"%s" % pattern, line, re.IGNORECASE):
                            help_text = self.append_module_to_reply(help_text, k, line)

        return help_text

    @respond_to("^help$")
    def help(self, message):
        """help: the normal help you're reading."""

        self.say("Sure thing, %s." % message.sender.nick, message=message)
        help_text = "Here's what I know how to do:"

        help_text = self.collect_help_modules(help_text)

        self.say(help_text, message=message, html=True)

    @respond_to("^help (?P<pattern>.*)")
    def help_pattern(self, message, pattern):
        """help ____: do not display all module helpers, only the ones which match"""

        help_text_header = "%s, you are probably looking for:" % message.sender.nick
        help_text = ""

        help_text = self.collect_help_modules(help_text, pattern)

        if help_text:
            self.say("%s %s" % (help_text_header, help_text), message=message, html=True)
        else:
            self.say("No match for your search, %s." % message.sender.nick, message=message)
