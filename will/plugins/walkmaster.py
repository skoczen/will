import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template

class WalkmasterPlugin(WillPlugin):

    @randomly(start_hour='10', end_hour='17', day_of_week="mon-fri", num_times_per_day=1)
    def walkmaster(self):
        now = datetime.datetime.now()
        in_5_minutes = now + datetime.timedelta(minutes=5)

        self.say("@all Walk happening in 5 minutes!")
        self.schedule_say("@all It's walk time!", in_5_minutes)


    @randomly(start_hour='11', end_hour='12', day_of_week="tue", num_times_per_day=58)
    def random_pings(self):
        now = datetime.datetime.now()
        self.say("Just a random thing at %s" % now)