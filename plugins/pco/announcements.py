from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate, pcoservices


class SchedulePlugin(WillPlugin):
    # @hear("announce")
    def announce_banana(self, message, channel="general"):
        self.say("announcing in: %s" % channel, channel=channel)
        AnnouncementPlugin.banana(self, message, channel=channel)


class AnnouncementPlugin(WillPlugin):
    # @periodic(hour='14', minute='10')  # at a certain time
    # @periodic(second=0)  # every minute at 0 seconds
    def announcetime(self):
        self.say("Announcement!", channel="general")

    # @hear("banana")
    def banana(self, message, channel=None):
        self.say("Bananaaaaa! %s" % channel, channel=channel)

    # @hear("this channel")
    def this_channel(self, message, channel=None):
        self.say("This channel's name is %s" % self.message.data.channel.name, channel=channel)
        self.say("This channel's id is %s" % self.message.data.channel.id, channel=channel)
