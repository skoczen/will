from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate, pcoservices


class ScheduledAnnounce(WillPlugin):

    # @hear("announce birthdays")
    # @periodic(hour='14', minute='10')  # at a certain time
    @periodic(hour='07', minute='50')  # at a certain time
    def announce_birthdays(self):
        birthday.announce_todays_birthdays(self, channel=self.announcement_channel())

    # @periodic(hour='14', minute='10')  # at a certain time
    # @periodic(second=0)  # every minute at 0 seconds
    @hear("(!announce)(?P<announcement>.*?(?=(?:\?)|$))", acl=["admins"])
    def announce(self, message, announcement):
        self.say("Announcement! %s" % announcement.strip(' '), channel=self.announcement_channel())

    # @hear("this channel")
    def this_channel(self, channel=None):
        self.say("This channel's name is %s" % self.message.data.channel.name, channel=self.announcement_channel())
        self.say("This channel's id is %s" % self.message.data.channel.id, channel=self.announcement_channel())

    @hear("(!toggle)(?P<toggle>.*?(?=(?:\?)|$))", acl=["admins"])
    def toggle_announcements(self, message, toggle):
        """!toggle Toggles what announcements will be sent `!toggle announcement`"""
        toggle = toggle.strip(' ')
        toggle = toggle.lower()
        toggle = toggle.replace(" ", "_")
        if self.load('announcement_toggles'):
            announcement_toggles = self.load('announcement_toggles')
            if toggle is '':
                self.reply("", attachments=self.get_toggles())
                return
            elif toggle:
                try:
                    announcement_toggles[toggle] = not announcement_toggles[toggle]
                    self.save('announcement_toggles', announcement_toggles)
                    self.reply("", message=message, attachments=self.get_toggles())
                except KeyError:
                    self.reply("Sorry I need the fully toggle name. Like `!toggle birthdays`", attachments=self.get_toggles())
        else:
            self.initialize_announcement_toggles()

    @hear("(!achannel)(?P<new_channel>.*?(?=(?:\?)|$))", acl=["admins"])
    def set_announcement_channel(self, message, new_channel):
        """!achannel Sets the channel announcements will be sent to. `!achannel #channel`"""

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
                    text="Announcement channel changed to %s" % self.get_slack_channel_link(new_channel_name))
        else:
            channel = self.load('announcement_channel')
            attachment = msg_attachment.SlackAttachment(
                fallback="Current announcement channel is %s" % channel,
                text="Current announcement channel is %s" % self.get_slack_channel_link(channel)
                )
        self.reply("", attachments=attachment.slack())

    def get_slack_channel_link(self, new_channel):
        """Retrieves a slack formated link from a channel name. This should probably be moved somewhere else."""
        channels = self.load("slack_channel_cache")
        channel = None
        for key in channels:
            # print(channels[key])
            if channels[key]['name'] == new_channel.strip(' '):
                # print(channels[key]['name'])
                channel = "<#%s|%s>" % (channels[key]['id'], channels[key]['name'])
        return channel

    def announcement_channel(self):
        """Used for retrieving the current announcement channel"""
        if self.load('announcement_channel'):
            channel = self.load('announcement_channel')
        else:
            self.save('announcement_channel', 'announcements')
            channel = 'announcements'
        return channel

    def initialize_announcement_toggles(self):
        announcement_toggles = {'birthdays': True,
                                'new_person_created': True}
        self.save('announcement_toggles', announcement_toggles)
        self.reply('Initilized Toggles!\n', attachments=self.get_toggles())
        return announcement_toggles

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

    def get_toggles(self):
        """Returns a string formated list of current announcement toggles"""
        announcement_toggles = self.load('announcement_toggles')
        toggle_msg = "\nCurrent Announcement Toggles:\n"
        for toggle, value in announcement_toggles.items():
            toggle_msg += ": ".join([toggle.replace("_", " ").title(),
                                     str(value).replace('False', 'Off').replace('True', 'On') + "\n"])
        toggle_attachment = msg_attachment.SlackAttachment(fallback=toggle_msg,
                                                           text=toggle_msg)
        return toggle_attachment.slack()
