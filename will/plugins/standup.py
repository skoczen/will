from will.plugin_base import WillPlugin
from will.decorators import respond_to, periodic, one_time_task, hear, randomly, route, rendered_template
from will import settings

class StandupPlugin(WillPlugin):

    @periodic(hour='10', minute='0', day_of_week="mon-fri")
    def standup(self):
        self.say("@all Standup! %s" % settings.WILL_HANGOUT_URL)
