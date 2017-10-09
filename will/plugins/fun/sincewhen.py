from datetime import datetime
from dateutil.relativedelta import relativedelta

from will.plugin import WillPlugin
from will.decorators import hear, respond_to


class SinceWhenPlugin(WillPlugin):

    @hear('Click here to join the video call')
    def hear_last_hipchat_video(self, messge):
        dt = datetime.now()
        self.save("last_hipchat_video", dt)

    @respond_to(r'\blast hipchat video\b')
    def when_last_hipchat_video(self, message):
        dt = datetime.now()
        ldt = self.load("last_hipchat_video")
        if ldt is not None:
            t_diff = relativedelta(dt, ldt)
            self.say("It's been %(days)s day(s) since any HipChat video was initiated." % {
                     'days': t_diff.days})
        else:
            self.say("So far no HipChat video was initiated", message=message)
