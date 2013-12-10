from will.plugin_base import WillPlugin
from will.decorators import respond_to, periodic, one_time_task, hear, randomly, route, rendered_template


class RosterPlugin(WillPlugin):

    @respond_to("who do you know about?")
    def list_roster(self, message):
        context = {"internal_roster": self.internal_roster.values(),}
        self.say(rendered_template("roster.html", context), message=message, html=True)
