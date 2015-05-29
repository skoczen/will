import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class PugPlugin(WillPlugin):

    @hear(r'\bpugs?\b')
    def talk_on_pug(self, message):
        req = requests.get('http://pugme.herokuapp.com/random')
        if req.ok:
            self.say(req.json()['pug'], message=message)
