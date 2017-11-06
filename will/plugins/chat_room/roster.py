from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class RosterPlugin(WillPlugin):

    @respond_to("who do you know about?")
    def list_roster(self, message):
        context = {"people": self.people.values(), }
        self.say(rendered_template("roster.html", context), message=message, html=True)
