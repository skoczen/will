import datetime
import requests
from will.plugin_base import WillPlugin
from will.decorators import respond_to, scheduled, one_time_task, hear, randomly, crontab, route, rendered_template
import will.settings as settings


class RosterPlugin(WillPlugin):

    @respond_to("who do you know about?")
    def list_roster(self, message):
        context = {"internal_roster": self.internal_roster.values(),}
        self.say(message, rendered_template("roster.html", context), html=True)
