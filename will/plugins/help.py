from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template


class HelpPlugin(WillPlugin):

    @respond_to("^help$")
    def help(self, message):
        help_data = self.load("help_files")
        print help_data
        self.say("Sure thing, %s." % message.sender.nick, message=message)
        help_text = "Here's what I know how to do:"
        for plugin_name, plugin_cmds in help_data:
            if plugin_cmds:
                help_text += "<br/>%s" % plugin_name
            for line in plugin_cmds:
                if line:
                    if ":" in line:
                        line = "<b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
                    help_text += "<li>%s</li>" % line

        self.say(help_text, message=message, html=True)
