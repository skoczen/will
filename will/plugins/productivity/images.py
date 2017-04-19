import random
import requests
from will import settings
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ImagesPlugin(WillPlugin):

    @respond_to("image me (?P<search_query>.*)$")
    def image_me(self, message, search_query):
        """image me ___ : Search google images for ___, and post a random one."""

        if not (getattr(settings, "GOOGLE_API_KEY", False) and getattr("GOOGLE_CUSTOM_SEARCH_KEY", False)):
            self.say(
                "Sorry, I'm missing my GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_KEY."
                " Can someone give them to me?", color="red"
            )
            return

        # https://developers.google.com/custom-search/json-api/v1/reference/cse/list?hl=en
        data = {
            "q": search_query,
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_CUSTOM_SEARCH_KEY,
            "safe": "medium",
            "num": 8,
            "searchType": "image",
        }
        r = requests.get("https://www.googleapis.com/customsearch/v1", params=data)
        r.raise_for_status()
        try:
            response = r.json()
            results = [result["link"] for result in response["items"] if "image" in r.json()]
        except TypeError:
            results = []
        if results:
            url = random.choice(results)
            self.say("%s" % url, message=message)
        else:
            self.say("Couldn't find anything!", message=message)
