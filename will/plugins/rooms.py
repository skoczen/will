from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class RoomsPlugin(WillPlugin):

    @respond_to("what are the rooms\?")
    def list_rooms(self, message):
        context = {"rooms": self.available_rooms.values(),}
        self.say(rendered_template("rooms.html", context), message=message, html=True)
