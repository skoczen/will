import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HerokuIsUpPlugin(WillPlugin):

    @periodic(second='46')
    def heroku_is_up(self):
        try:
            r = requests.get("https://status.heroku.com/api/v3/current-status")
            last_status = self.load("last_heroku_status")
            if last_status and r.json()["status"] != last_status:
                if r.json()["status"]["Production"] != "green":
                    self.say(
                        "FYI everyone, heroku is having trouble: %s. \n "
                        "http://status.heroku.com" % r.json()["issues"][0]["title"]
                    )
                else:
                    self.say("Looks like heroku's back up!")
                self.save("last_heroku_status", r.json()["status"])
        except:
            pass
