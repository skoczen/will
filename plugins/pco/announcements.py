from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate


class AnnouncementPlugin(WillPlugin):
    @periodic(hour='11', minute='45')
    def announcetime(self):
        self.say("It's 11:45 AM!", channel="announcements")
