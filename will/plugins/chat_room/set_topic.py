from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class NewTopicPlugin(WillPlugin):

    @respond_to("^(?:new|set)?\s?(?:the|room|the\sroom)?\s?topic[ :=,;]*(?P<topic>.*)$", allowed_typos=2)
    def new_topic(self, message, topic="Something or other. You weren't terribly specific."):
        """set topic ___: Set the room topic to ___."""
        self.set_topic(topic, message=message)
