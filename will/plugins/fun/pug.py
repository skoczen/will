import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class PugPlugin(WillPlugin):

    @hear(r'\bpugs?\b')
    def talk_on_pug(self, message):
        req = requests.get('http://pugme.herokuapp.com/random')
        if req.ok:
            pug = req.json()['pug']

            if 'media.tumblr.com' in pug:
                # replace *.media.tumblr.com with media.tumblr.com and force ssl
                pug = 'https://media.tumblr.com' + pug.split('media.tumblr.com')[1]

            self.say(pug, message=message)
