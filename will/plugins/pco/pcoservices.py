from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will.plugins.pco import set_list


class PcoServicesPlugin(WillPlugin):
    @hear("(?:do you |find |got |a )?(set list for |!setlist |setlist for |!sunday |songs for |order of service for )"
          "(?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_setlist_lookup(self, message , pco_date):
        self.reply("Let me get that for you.")
        setList = set_list.get(pco_date)
        if setList is None:
            self.reply("Sorry I don't have " + setList + "'s set list.")
        # print(setList)
        self.reply(setList)


# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':

    print("Getting set list for 'Sunday'")
    set('sunday')
