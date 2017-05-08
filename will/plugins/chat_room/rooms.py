from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class RoomsPlugin(WillPlugin):

    @respond_to("what are the rooms\?")
    def list_rooms(self, message):
        """what are the rooms?: List all the rooms I know about."""
        context = {"rooms": self.available_rooms.values(), }
        self.say(rendered_template("rooms.html", context), message=message, html=True)

    @respond_to("^update the room list")
    def update_rooms(self, message):
        self.update_available_rooms()
        self.say("Done!", message=message)

    @respond_to("who is in this room\?")
    def participants_in_room(self, message):
        """who is in this room?: List all the participants of this room."""
        room = self.get_room_from_message(message)
        context = {"participants": room.participants, }
        self.say(rendered_template("participants.html", context), message=message, html=True)
