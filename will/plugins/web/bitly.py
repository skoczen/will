# coding: utf-8


import bitly_api   # pip install bitly_api

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


def get_bitly_shorten_url(long_url):
    """
    Function to get shorten_url from bit.ly through API
    """
    BITLY_ACCESS_TOKEN = ' <get_access_token_from_bitly.com> '
    # use oauth2 endpoints
    c = bitly_api.Connection(access_token=BITLY_ACCESS_TOKEN)
    response = c.shorten(uri=long_url)
    return response['url']


class BitlyPlugin(WillPlugin):
    """
    Class for creating Bitly shorten URL's.
    """
    
    @respond_to("^bitly (?P<long_url>.*)$")
    def say_bitly_short_url(self, message, long_url, short_url=None):
        short_url = get_bitly_shorten_url(long_url)
        self.reply("Shorten URL: %s" % short_url, message=message)

