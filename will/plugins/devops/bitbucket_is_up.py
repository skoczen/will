import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class BitBucketIsUpPlugin(WillPlugin):

    @periodic(second='36')
    def bitbucket_is_up(self):
        try:
            r = requests.get("http://bqlf8qjztdtr.statuspage.io/api/v2/status.json")
            last_status = self.load("last_bb_status")
            if last_status and r.json()["status"]["indicator"] != last_status:
                if r.json()["status"]["indicator"] != "none":
                    self.say("FYI everyone, Bitbucket is having trouble: %s" % r.json()["status"]["description"])
                else:
                    self.say("Looks like Bitbucket's back up!")
                self.save("last_bb_status", r.json()["status"]["indicator"])
        except:
            pass
