from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

import requests


class RandomTopicPlugin(WillPlugin):

    # @respond_to("new topic")
    def give_us_somethin_to_talk_about(self, message):
        # """new topic: set the room topic to a random conversation starter."""
        r = requests.get("http://www.chatoms.com/chatom.json?Normal=1&Fun=2&Philosophy=3&Out+There=4")
        data = r.json()
        self.set_topic(data["text"], message=message)
