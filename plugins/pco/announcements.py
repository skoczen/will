from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate, pcoservices


class ScheduledAnnounce(WillPlugin):

    # @hear("announce birthdays")
    # @periodic(hour='14', minute='10')  # at a certain time
    @periodic(hour='07', minute='50')  # at a certain time
    def announce_birthdays(self, channel='announcements'):
        birthday.announce_todays_birthdays(self, channel=channel)

    # @periodic(hour='14', minute='10')  # at a certain time
    # @periodic(second=0)  # every minute at 0 seconds
    def announce(self):
        self.say("Announcement!", channel="general")

    # @hear("this channel")
    def this_channel(self, channel=None):
        self.say("This channel's name is %s" % self.message.data.channel.name, channel=channel)
        self.say("This channel's id is %s" % self.message.data.channel.id, channel=channel)
