import datetime
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class RemindMePlugin(WillPlugin):

    @respond_to("remind me to (?P<reminder_text>.*?) (at|on) (?P<remind_time>.*)")
    def remind_me_at(self, message, reminder_text=None, remind_time=None):
        """remind me to ___ at ___: Set a reminder for a thing, at a time."""
        now = datetime.datetime.now()
        parsed_time = self.parse_natural_time(remind_time)
        natural_datetime = self.to_natural_day_and_time(parsed_time)

        formatted_reminder_text = "@%(from_handle)s, you asked me to remind you %(reminder_text)s" % {
            "from_handle": message.sender.nick,
            "reminder_text": reminder_text,
        }
        self.schedule_say(formatted_reminder_text, parsed_time, message=message)
        self.say("%(reminder_text)s %(natural_datetime)s. Got it." % locals(), message=message)
