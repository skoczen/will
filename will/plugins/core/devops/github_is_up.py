import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class ServicesPlugin(WillPlugin):

    @periodic(second='36')
    def github_is_up(self):
        r = requests.get("https://status.github.com/api/last-message.json")
        last_status = self.load("last_github_status")
        if r.json()["status"] != last_status:
            if r.json()["status"] != "good":
                self.say("FYI everyone, github is having trouble: %s" % r.json()["body"])
            else:
                self.say("Looks like github's back up!")
            self.save("last_github_status", r.json()["status"])
