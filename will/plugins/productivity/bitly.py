# coding: utf-8


import bitly_api   # pip install bitly_api

from will.plugin import WillPlugin
from will.decorators import (respond_to, periodic, hear, randomly, route,
                             rendered_template, require_settings)

from will import settings


# BITLY_ACCESS_TOKEN = ' <get_access_token_from_bitly.com> '


class BitlyPlugin(WillPlugin):
    """Class for creating Bitly shorten URL's."""

    @respond_to("^bitly (?P<long_url>.*)$")
    @require_settings("BITLY_ACCESS_TOKEN",)
    def get_bitly_shorten_url(self, message, long_url, short_url=None):
        """Function to get shorten_url from bit.ly through API."""
        # use oauth2 endpoints
        c = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)
        response = c.shorten(uri=long_url)
        short_url = response['url']
        self.reply("Shorten URL: %s" % short_url, message=message)
