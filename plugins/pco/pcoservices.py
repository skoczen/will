from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import song_info, authenticate, set_list, teams
from will.mixins.slackwhitelist import wl_chan_id

app = "services"


# I turned off credentials for this because it's not sensitive info.
class PcoServicesPlugin(WillPlugin):
    @respond_to("(?:do you |find |got |a )?(set list for |!setlist|setlist for |"
                "!sunday |songs for |order of service for )(?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_setlist_lookup(self, message, pco_date):
        if pco_date is "":
            pco_date = 'sunday'
        """set list for Sunday: tells you the set list for a certain date"""
        attachment = []
        self.reply("Let me get that for you. This might take a bit if you have a lot of services.")
        for x in set_list.get(pco_date):
            attachment += x.slack()
        if attachment:
            self.reply("", message=message, attachments=attachment)
        else:
            self.reply("Sorry I don't find any set lists scheduled on" + pco_date + " in Services.")

    @respond_to("(?:what is |show me |what's |a )?(song list for |!songlist|!checksongs|!setsongs|!songcheck)"
                "(?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_setlist_songs(self, message, pco_date):
        if pco_date is "":
            pco_date = 'sunday'
        self.reply("Let me get that song list for you.")
        song_list = set_list.get_set_songs(pco_date)
        attachment = []
        for result in song_list:
            attachment += result.slack()
        if attachment:
            self.reply("Here's the songs scheduled for " + pco_date, message=message, attachments=attachment)
        else:
            self.reply("Sorry I don't find any songs scheduled on " + pco_date + " in Services.")

    @respond_to("(?:what is |show me |what's |a )?(arrangement for |!song )(?P<pco_song>.*?(?=(?:\'|\?)|$))")
    def pco_song_lookup(self, message, pco_song):
        """arrangement for [song]: tells you the arrangement for a certain song"""
        self.reply("Let me get that song for you.")
        song = song_info.get(pco_song)
        attachment = []
        for result in song:
            attachment += result.slack()
        if attachment is None:
            self.reply("Sorry I don't find " + song + "in services.")
        self.reply("", message=message, attachments=attachment)

    @respond_to("(!teams|!team) (?P<pco_team>.*?(?=(?:\?)|$))")
    def pco_team_lookup(self, message, pco_team):
        """!team <team name>: returns a list of people serving on the team"""
        pco_team = pco_team.strip()
        if not pco_team:
            self.reply("Hold on I'll look up the teams for you.")
        else:
            self.reply("Hold on I'll look up that team for you.")
        team_list = teams.get(pco_team)
        attachment = []
        for result in team_list:
            attachment += result.slack()
        if not attachment:
            self.say('Sorry I don\'t find a team named "' + pco_team + '" in services.', channel=wl_chan_id(self))
        else:
            self.say("", message=message, attachments=attachment, channel=wl_chan_id(self))

    @respond_to("who is (serving|scheduled) (on|for)( the)? (?P<pco_team>[\w ]+) team\s?(?P<pco_date>.*?(?=(?:\'|\?)|$))\??")
    def pco_team_schedule_lookup(self, message, pco_team, pco_date):
        """ "who is serving|scheduled on the <team name> team <date>": looks up a [team name] and displays its confirmed and
        unconfirmed members for a given date"""
        pco_team = pco_team.strip()
        self.reply("Hold on; I'll look up that team's schedule for you.")
        if pco_date.strip() == '':
            pco_date = 'today'
        attachments = teams.get_for_date(pco_team, pco_date)
        attachment = []
        for returned_attachment in attachments:
            attachment += returned_attachment.slack()
        self.say("", message=message, attachments=attachment, channel=wl_chan_id(self))

    @respond_to("(!serving|!scheduled) ((\"|\')(?P<pco_team>[\w ]+)(\"|\')|(?P<pco_team_unquoted>[\w]+)) (?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_team_schedule_lookup_command(self, message, pco_team, pco_team_unquoted, pco_date):
        """!serving | !scheduled <team name> <date>: : looks up a [team name] and displays its confirmed and
        unconfirmed members for a given date"""
        if pco_team.strip() == '':
            pco_team = pco_team_unquoted
        self.pco_team_schedule_lookup(message, pco_team, pco_date)

    @respond_to("!notify-team (?P<pco_team>[\w ]+) in channel (?P<channel>[\w]+)")
    def add_team_notification(self, message, pco_team, channel):
        teams.add_team_notification(self, pco_team, channel)
        self.say('Team notifications turned on for {} in the {} channel.'.format(pco_team, channel))

    @respond_to("!remove-notification (?P<pco_team>[\w ]+)")
    def remove_team_notification(self, message, pco_team):
        success = teams.remove_team_notification(self, pco_team.strip())
        if success:
            self.say('Removed notification for {}.'.format(pco_team))
        else:
            self.say('Could not find specified team. Check `!team-notifications` to see teams with notifications.')

    @respond_to("!team-notifications")
    def show_team_notifications(self, message):
        attachment = []
        attachments = teams.get_team_notifications(self)
        for returned_attachment in attachments:
            attachment += returned_attachment.slack()
        self.say('', message=message, attachments=attachment)

    @periodic(minute='*/15')
    def test_every_15(self):
        watched_teams = teams.team_notification_list(self)
        for team in watched_teams:
            is_scheduled, confirmed_attachment = teams.team_is_scheduled(team)
            if is_scheduled:
                attachment = []
                attachments = confirmed_attachment
                for returned_attachment in attachments:
                    attachment += returned_attachment.slack()
                self.say('', channel=watched_teams[team], attachments=attachment)


# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    date = "sunday"
    song_name = "Mighty to Save"
    team_name = "Audio/Visual"
    # print("Getting set list for ", date)
    # for x in set_list.get(date):
    #     print(x.txt())
    # print("Getting song info for ", song_name)
    # for x in song_info.get(song_name):
    #     print(x.txt())
    # print("Getting this weeks songs.")
    # for attachment in set_list.get_set_songs(date):
    #     print(attachment.txt())
    print("Getting the team list")
    for attachment in teams.get(team_name):
        print(attachment.txt())
