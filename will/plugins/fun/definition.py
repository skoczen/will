from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
import requests


class DefinitionPlugin(WillPlugin):
    @respond_to("^urban dictionary (?P<word>.*)$")
    def definition(self, message, word):
        r = requests.get("http://api.urbandictionary.com/v0/define?term={0}".format(word))
        wordlist = r.json()
        if wordlist['result_type'] == 'exact':
            def1 = wordlist['list'][0]['definition']
            ex1 = wordlist['list'][0]['example']
            context = {
                "word": word.title(),
                "definition": self.stripchars(def1, "[]"),
                "example": self.stripchars(ex1, "[]"),
            }
            self.say(rendered_template("urban_define.html", context), message, html=True)
        else:
            self.say("No definition found for {0}.\nSorry homie.".format(word), message=message)

    # Strips characters from a string.
    def stripchars(self, s, chars):
        return "".join(c for c in s if c not in chars)
