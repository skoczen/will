# coding: utf-8


import bitly_api   # pip install bitly_api

from will.plugin import WillPlugin
from will.decorators import (respond_to, periodic, hear, randomly, route,
                             rendered_template, require_settings)

from will import settings


# BITLY_ACCESS_TOKEN = ' <get_access_token_from_bitly.com> '


class BitlyPlugin(WillPlugin):

    @require_settings("BITLY_ACCESS_TOKEN",)
    def get_bitly_shorten_url(self, long_url):
        """Function to get shorten_url from bit.ly through API."""
        # use oauth2 endpoints
        c = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)
        response = c.shorten(uri=long_url)
        return response['url']

    @respond_to("^bitly (?P<long_url>.*)$")
    def say_bitly_short_url(self, message, long_url, short_url=None):
        """bitly ___: Shorten long_url using bitly service."""
        short_url = self.get_bitly_shorten_url(long_url)
        self.say("Shorten URL: %s" % short_url, message=message)