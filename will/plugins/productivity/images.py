import random
import requests
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ImagesPlugin(WillPlugin):

    @respond_to("image me (?P<search_query>.*)$")
    def image_me(self, message, search_query):
        """image me ___ : Search google images for ___, and post a random one."""
        data = {
            "q": search_query,
            "v": "1.0",
            "safe": "active",
            "rsz": "8"
        }
        r = requests.get("http://ajax.googleapis.com/ajax/services/search/images", params=data)
        results = r.json()["responseData"]["results"]
        if len(results) > 0:
            url = random.choice(results)["unescapedUrl"]
            self.say("%s" % url, message=message)
        else:
            self.say("Couldn't find anything!", message=message)