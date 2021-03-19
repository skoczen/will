from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

MAX_LINES = 18


class ProgrammerHelpPlugin(WillPlugin):

    @respond_to("^programmer help$")
    def help(self, message):
        """programmer help: Advanced programmer-y help."""
        all_regexes = self.load("all_listener_regexes")
        self.say("Here's everything I know how to listen to:", message, start_thread=True)
        for r in range(0, len(all_regexes), MAX_LINES):
            text = "\n".join(all_regexes[r:r+MAX_LINES])
            self.say(f'```{text}```', message, start_thread=True)
