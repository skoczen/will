from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate


class AnnouncementPlugin(WillPlugin):
    @periodic(hour='14', minute='00')
    # @periodic(second=0)
    def announcetime(self):
        self.say("2 PM!", channel="general")
