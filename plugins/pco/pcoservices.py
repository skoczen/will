from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import song_info, authenticate, set_list

app = "services"


class PcoServicesPlugin(WillPlugin):
    # I turned off credentials for this because it's not sensitive info.
    @respond_to("(?:do you |find |got |a )?(set list for |!setlist |setlist for |"
                "!sunday |songs for |order of service for )(?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_setlist_lookup(self, message, pco_date):
        """set list for Sunday: tells you the set list for a certain date"""
        # credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        # if authenticate.get(credentials, app):
        attachment = []
        self.reply("Let me get that for you. This might take a bit if you have a lot of services.")
        for x in set_list.get(pco_date):
            attachment += x.slack()
        self.reply("", message=message, attachments=attachment)
        # else:
        #     self.reply("Sorry but you don't have access to the Services App. "
        #                "Please contact your administrator.")

    @respond_to("(?:what is |show me |what's |a )?(arrangement for |!song )(?P<pco_song>.*?(?=(?:\'|\?)|$))")
    def pco_song_lookup(self, message, pco_song):
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            self.reply("Let me get that song for you.")
            song = song_info.get(pco_song)
            attachment = song.slack()
            if attachment is None:
                self.reply("Sorry I don't find " + song + "in services.")
            self.reply("", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the Services App. "
                       "Please contact your administrator.")

# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    date = "sunday"
    song_name = "Mighty to Save"
    print("Getting set list for ", date)
    for x in set_list.get(date):
        print(x.txt())
    print("Getting song info for ", song_name)
    print(song_info.get(song_name).txt())
