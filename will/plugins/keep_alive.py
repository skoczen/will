import datetime
import requests
from will.plugin_base import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template
import will.settings as settings


class KeepAlivePlugin(WillPlugin):

    @periodic(second=0)
    def ping_keep_alive(self):
        requests.get("%s/keep-alive" % settings.WILL_URL)

    @route("/keep-alive")
    def keep_alive(self):
        return rendered_template("keep_alive.html", {})

    @route("/ping")
    def ping(self):
        self.say("Someone pinged me!")
        return "PONG"
