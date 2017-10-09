import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HipChatIsUpPlugin(WillPlugin):

    @periodic(second='36')
    def hipchat_is_up(self):
        try:
            r = requests.get("https://status.hipchat.com/api/v2/status.json")
            last_status = self.load("last_hipchat_status")
            if last_status and r.json()["status"]["indicator"] != last_status:
                if r.json()["status"]["indicator"] != "none":
                    self.say("FYI everyone, HipChat is having trouble: %s" % r.json()["status"]["description"])
                else:
                    self.say("Looks like HipChat's back up!")
                self.save("last_hipchat_status", r.json()["status"]["indicator"])
        except:
            pass
