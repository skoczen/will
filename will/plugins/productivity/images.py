import logging
import random
import requests
from will import settings
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ImagesPlugin(WillPlugin):

    @respond_to("image me (?P<search_query>.*)$")
    def image_me(self, message, search_query):
        """image me ___ : Search google images for ___, and post a random one."""

        if (
                getattr(settings, "GOOGLE_API_KEY", False) and
                getattr(settings, "GOOGLE_CUSTOM_SEARCH_ENGINE_ID", False)
        ):
            self.say(
                "Sorry, I'm missing my GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID."
                " Can someone give them to me?", color="red"
            )
            # https://developers.google.com/custom-search/json-api/v1/reference/cse/list?hl=en
            data = {
                "q": search_query,
                "key": settings.GOOGLE_API_KEY,
                "cx": settings.GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
                "safe": "medium",
                "num": 8,
                "searchType": "image",
            }
            r = requests.get("https://www.googleapis.com/customsearch/v1", params=data)
            r.raise_for_status()
            try:
                response = r.json()
                results = [result["link"] for result in response["items"] if "items" in r.json()]
            except TypeError:
                results = []
        else:
            # Fall back to a really ugly hack.
            logging.warn(
                "Hey, I'm using a pretty ugly hack to get those images, and it might break. "
                "Please set my GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID when you have a chance."
            )
            r = requests.get("https://www.google.com/search?tbm=isch&safe=active&q=%s" % search_query)
            results = []
            content = r.content.decode("utf-8")
            index = content.find("<img")
            while index != -1:
                src_start = content.find('src=', index)
                src_end = content.find(" ", src_start)
                match = content[src_start+5: src_end-1]

                index = content.find("<img", src_end)
                results.append(match)
        if results:
            url = random.choice(results)
            self.say("%s" % url, message=message)
        else:
            self.say("Couldn't find anything!", message=message)

    @respond_to("gif me (?P<search_query>.*$)")
    def gif_me(self, message, search_query):

        if (
                getattr(settings, "GOOGLE_API_KEY", False) and
                getattr(settings, "GOOGLE_CUSTOM_SEARCH_ENGINE_ID", False)
        ):
            self.say(
                "Sorry, I'm missing my GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID."
                " Can someone give them to me?", color="red"
            )
            # https://developers.google.com/custom-search/json-api/v1/reference/cse/list?hl=en
            data = {
                "q": search_query,
                "key": settings.GOOGLE_API_KEY,
                "cx": settings.GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
                "safe": "medium",
                "num": 8,
                "searchType": "image",
                "imgType": "animated",
            }
            r = requests.get("https://www.googleapis.com/customsearch/v1", params=data)
            r.raise_for_status()
            try:
                response = r.json()
                results = [result["link"] for result in response["items"] if "items" in r.json()]
            except TypeError:
                results = []
        else:
            # Fall back to a really ugly hack.
            logging.warn(
                "Hey, I'm using a pretty ugly hack to get those images, and it might break. "
                "Please set my GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID when you have a chance."
            )
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            }
            r = requests.get("https://www.google.com/search?tbm=isch&tbs=itp:animated&safe=active&q=%s" % search_query, headers=headers)
            results = []
            content = r.content.decode("utf-8")
            index = content.find('"ou":')
            while index != -1:
                src_start = content.find('"ou":', index)
                src_end = content.find('","', src_start)
                match = content[src_start+6: src_end]

                index = content.find('"ou":', src_end)
                results.append(match)
        if results:
            url = random.choice(results)
            self.say("%s" % url, message=message)
        else:
            self.say("Couldn't find anything!", message=message)
