import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class TimePlugin(WillPlugin):

    @respond_to("what time is it")
    def what_time_is_it(self, message):
        now = datetime.datetime.now()
        self.say("It's %s." % self.to_natural_day_and_time(now), message=message)
