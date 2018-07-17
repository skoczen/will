import requests
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class TalkBackPlugin(WillPlugin):
    QUOTES_URL = "https://underquoted.herokuapp.com/api/v2/quotations/?random=true&limit=1"

    def get_quote(self):
        quote = None
        response = requests.get(self.QUOTES_URL)
        if response.status_code == 200:
            try:
                quote_obj = response.json()['results'][0]
                quote = u'%s ~ %s' % (quote_obj['text'], quote_obj['author'])
            except ValueError:
                raise Exception(
                    "Response from '%s' could not be decoded as JSON:\n%s"
                    % (self.QUOTES_URL, response)
                )
            except KeyError as e:
                raise Exception(
                    "Response from '%s' did not contain field: %s\n%s"
                    % (self.QUOTES_URL, e, response)
                )

        else:
            raise Exception(
                "Got an error from '%s': %s\n%s"
                % (self.QUOTES_URL, response.status_code, response)
            )
        return quote

    # @hear("that'?s what she said")
    def talk_back(self, message):
        # """that's what she said: Tells you some things she actually said. :)"""
        quote = self.get_quote()
        if quote:
            self.reply("Actually, she said things like this: \n%s" % quote)
