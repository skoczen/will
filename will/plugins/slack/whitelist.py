from will.plugin import WillPlugin
from will.decorators import hear
from will.mixins.slackwhitelist import whitelist_remove, whitelist_add, wl_chan_id, whitelist_list, wl_check, \
    whitelist_wipe


# This is a group of commands for administering the Slack Channel Whitelist.
# It defaults to the admin acl group.
class WhitelistPlugin(WillPlugin):

    # Adds a channel to the whitelist
    # (?P<channel_name>.*?(?=(?:$)))
    @hear("(!wladd)(?P<channel>.*?(?=(?:\?)|$))", acl=["admins"])
    def wl_adder(self, message, channel):
        if channel:
            whitelist_add(self, channel_name=channel.strip())
        else:
            whitelist_add(self)

    # Removes a channel from the whitelist
    @hear("(!wlremove)(?P<channel>.*?(?=(?:\?)|$))", acl=["admins"])
    def wl_remover(self, message, channel):
        if channel:
            whitelist_remove(self, channel_name=channel.strip())
        else:
            whitelist_remove(self)

    # Sends the current whitelist to the Slack user as a DM
    @hear("(!whitelist)", acl=["admins"])
    def whitelist_lister(self, message):
        whitelist_list(self)

    # Demonstrates how to use the wl_check method to test if a channel is whitelisted.
    @hear("(!wlcheck)", acl=["admins"])
    def whitelist_checker(self, message):
        if wl_check(self):
            self.reply("This channel is whitelisted!")
        else:
            self.reply("This channel is not whitelisted.")

    # Demonstrates how to use the wl_chan_id method to easily add whitelisting to an existing command.
    @hear("(!wlchan)", acl=["admins"])
    def whitelist_channel(self, message):
        # NOTE You need to use self.say for this to work!
        self.say("This response goes to the channel if it is a whitelisted channel, "
                 "but goes to a DM if the channel isn't whitelisted.", channel=wl_chan_id(self))

    # Testing function for wiping the whitelist
    @hear("(!wlwipe)", acl=["admins"])
    def whitelist_wipe(self, message):
        # NOTE You need to use self.say for this to work!
        if not self.load("whitelist"):
            whitelist_wipe(self)
        self.reply("Whitelist Wiped!", message=message)
