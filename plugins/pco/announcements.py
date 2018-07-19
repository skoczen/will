from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate


class AnnouncementPlugin(WillPlugin):
    # @periodic(hour='14', minute='10')  # at a certain time
    # @periodic(second=0)  # every minute at 0 seconds
    def announcetime(self):
        self.say("Announcement!", channel="general")
