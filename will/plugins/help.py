from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route,\
 rendered_template, user_help
from sets import Set


class HelpPlugin(WillPlugin):
    @user_help(invocation="help", action="shows available user commands")
    @respond_to("^help$")
    def help(self, message, search_phrase=None, request_hidden=False):
        help_data = self.load("help_files")
        help_text = ""
        if search_phrase:
            #eventually stop_words can expand, but rather underfilter right now than overfilter
            stop_words=Set(['it','the','a','with','in','on','to'])
            search_terms = Set(search_phrase.split(" ")) - stop_words
        else:
            search_terms= [""]
        for plugin in help_data:
            cmd_text = []
            for cmd in plugin["commands"]:
                skip = True
                invocation = cmd["regex"]
                action = cmd["function_name"]
                if "user_help" in cmd:
                    user_help = cmd["user_help"]
                    hidden = user_help["hidden"]
                    if user_help["invocation"]:
                        invocation = user_help["invocation"]
                    if user_help["action"]:
                        action = user_help["action"]
                ### START DEPRECATED __doc__ behaviors
                # note once we remove this, will want to use __doc__ as a default for the action field
                else:
                    if not cmd["doc"]:
                        hidden = True
                    else:
                        hidden = False
                        if request_hidden == True:
                            # just for backward compatability
                            # we used to equate __doc__ strings to info not for programmers!
                            continue
                        print "DEPRECATED: use @user_help instead of __doc__ for %s" % cmd['function_name']
                        for term in search_terms:
                            if term in cmd["doc"]:
                                skip = False
                                break
                        if not skip:
                            line = cmd["doc"]
                            if ':' in line:
                                line = "<b>%s</b>%s" % (line[:line.find(":")], line[line.find(":"):])
                            cmd_text.append("<li>%s</li>" % line)
                        else:
                            print "skipping %s because no match" % action
                        continue
                ### END DEPRECATED __doc__ behaviors
                 
                if request_hidden != hidden:
                    print "skipping %s because hidden" % action
                    continue
                for term in search_terms:
                    if term in action or term in invocation:
                        skip = False 
                        break
                if skip == True:
                    continue
                cmd_text.append("<li><b>%s</b>: %s</li>" % (invocation, action))
            if cmd_text:
                help_text += "<br/>%s%s" % (plugin["name"], "".join(cmd_text))
        if help_text == "":
            self.say("Sorry, I don't know anything about that yet.", message=message)
        else:
            self.say(help_text, message=message, html=True)

    @user_help(invocation="help on [word or phrase]", action="shows related user commands")
    @respond_to("^help on (?P<search_phrase>.*)")
    def help_on(self, message, search_phrase):
        self.help(message, search_phrase=search_phrase)

    @user_help(invocation="programmer help", action="shows programmer commands")
    @respond_to("^programmer help$")
    def programmer_help(self, message):
        self.help(message, request_hidden=True)

    @user_help(invocation="programmer help on [word or phrase]", action="shows related programmer commands")
    @respond_to("^programmer help on (?P<search_phrase>.*)")
    def programmer_help_on(self, message, search_phrase):
        self.help(message, search_phrase=search_phrase, request_hidden=True)
