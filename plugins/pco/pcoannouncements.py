from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, msg_attachment, announcements, giving_report
import logging


class ScheduledAnnounce(WillPlugin):

    # @hear("announce birthdays")
    # @periodic(hour='14', minute='10')  # at a certain time
    @periodic(hour='07', minute='50')  # at a certain time
    def announce_birthdays(self):
        if announcements.announcement_is_enabled(self, announcement='birthdays'):
            birthday.announce_todays_birthdays(self, channel=announcements.announcement_channel(self))

    @periodic(day='Sunday', hour='15')
    # @periodic(second=0)
    # @hear("(!test_giving)", acl=["admins"])
    def report_giving(self, message):
        # if announcements.announcement_is_enabled(self, announcement='giving'):
        g_report = giving_report.get_giving(report_date="Last Monday")
        for g in g_report:
            attachment = g.slack()
        self.say("Giving Report", attachments=attachment, channel='giving')

    @hear("(!test_giving)", acl=["admins"])
    def report_giving(self, message):
        # if announcements.announcement_is_enabled(self, announcement='giving'):
        g_report = giving_report.get_giving(report_date="Last Monday")
        for g in g_report:
            attachment = g.slack()
        self.say("Giving Report", attachments=attachment, channel='giving')

    # @periodic(hour='14', minute='10')  # at a certain time
    # @periodic(second=0)  # every minute at 0 seconds
    @hear("(!announce)(?P<announcement>.*?(?=(?:\?)|$))", acl=["admins"])
    def announce(self, message, announcement):
        self.say("Announcement! %s" % announcement.strip(' '), channel=announcements.announcement_channel(self))

    # @hear("this channel")
    def this_channel(self, channel=None):
        self.say("This channel's name is %s" % self.message.data.channel.name,
                 channel=announcements.announcement_channel(self))
        self.say("This channel's id is %s" % self.message.data.channel.id,
                 channel=announcements.announcement_channel(self))

    @hear("(!toggle)(?P<toggle>.*?(?=(?:\?)|$))", acl=["admins"])
    def toggle_announcements(self, message, toggle):
        """!toggle: Toggles what announcements will be sent. Use !toggle without an
        announcement name to get a list of current toggles."""
        toggle = toggle.strip(' ')
        toggle = toggle.lower()
        toggle = toggle.replace(" ", "_")
        if self.load('announcement_toggles'):
            announcement_toggles = self.load('announcement_toggles')
            if toggle is '':
                self.reply("", attachments=announcements.get_toggles(self))
                return
            elif toggle:
                try:
                    announcement_toggles[toggle] = not announcement_toggles[toggle]
                    self.save('announcement_toggles', announcement_toggles)
                    self.reply("", message=message, attachments=announcements.get_toggles(self))
                except KeyError:
                    self.reply("Sorry I need the full toggle name. Like `!toggle birthdays`",
                               attachments=announcements.get_toggles(self))
        else:
            announcements.initialize_announcement_toggles(self)

    @hear("(!achannel)(?P<new_channel>.*?(?=(?:\?)|$))", acl=["admins"])
    def set_announcement_channel(self, message, new_channel):
        """!achannel: Sets the channel announcements will be sent to. `!achannel #channel`"""

        if new_channel:
            try:
                new_channel = new_channel.split('|')[1]
            except Exception as e:
                print(type(e))

            finally:
                new_channel_name = new_channel.strip('# >')
                print("NEW CHANNEL IS : %s" % new_channel)
                self.save('announcement_channel', new_channel_name)
                attachment = msg_attachment.SlackAttachment(
                    fallback="Announcement channel changed to %s" % new_channel_name,
                    text="Announcement channel changed to %s"
                         % announcements.get_slack_channel_link(self, new_channel_name))
        else:
            channel = self.load('announcement_channel')
            attachment = msg_attachment.SlackAttachment(
                fallback="Current announcement channel is %s" % channel,
                text="Current announcement channel is %s"
                     % announcements.get_slack_channel_link(self, new_channel=channel)
                )
        self.reply("", attachments=attachment.slack())

    # Testing function for wiping the announcement_toggles
    @hear("(!twipe)", acl=["admins"])
    def toggle_wipe(self, message):
        if self.load("announcement_toggles"):
            try:
                self.clear("announcement_toggles")
            except Exception as e:
                self.reply("There isn't an announcement toggle list to clear.")
            finally:
                self.reply("Announcement Toggles Wiped!", message=message)
