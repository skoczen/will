from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class RoomsPlugin(WillPlugin):

    @respond_to("what are the rooms\?")
    def list_rooms(self, message):
        """what are the rooms?: List all the rooms I know about."""
        context = {"rooms": self.available_rooms.values(),}
        self.say(rendered_template("rooms.html", context), message=message, html=True)


    @respond_to("^update the room list")
    def update_rooms(self, message):
        self.update_available_rooms()
        self.say("Done!", message=message)
