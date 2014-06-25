from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class NewTopicPlugin(WillPlugin):

    @respond_to("(?:new|set) topic (?P<topic>.*)")
    def new_topic(self, message, topic="Something or other. You weren't terribly specific."):
        """set topic ___: Set the room topic to ___."""
        self.set_topic(topic, message=message)
