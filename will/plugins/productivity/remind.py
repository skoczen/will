from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class RemindPlugin(WillPlugin):

    @respond_to("(?:can |will you )?remind me(?P<to_string> to)? (?P<reminder_text>.*?) (at|on|in) (?P<remind_time>.*)?\??")
    def remind_me_at(self, message, reminder_text=None, remind_time=None, to_string=""):
        """remind me to ___ at ___: Set a reminder for a thing, at a time."""
        parsed_time = self.parse_natural_time(remind_time)
        natural_datetime = self.to_natural_day_and_time(parsed_time)
        if to_string:
            formatted_to_string = to_string
        else:
            formatted_to_string = ""
        formatted_reminder_text = "%(mention_handle)s, you asked me to remind you%(to_string)s %(reminder_text)s" % {
            "mention_handle": message.sender.mention_handle,
            "from_handle": message.sender.handle,
            "reminder_text": reminder_text,
            "to_string": formatted_to_string,
        }
        self.schedule_say(formatted_reminder_text, parsed_time, message=message, notify=True)
        self.say("%(reminder_text)s %(natural_datetime)s. Got it." % locals(), message=message)

    @respond_to("(?:can|will you )?remind (?P<reminder_recipient>(?!me).*?)(?P<to_string> to>) ?(?P<reminder_text>.*?) (at|on|in) (?P<remind_time>.*)?\??")
    def remind_somebody_at(self, message, reminder_recipient=None, reminder_text=None, remind_time=None, to_string=""):
        """remind ___ to ___ at ___: Set a reminder for a thing, at a time for somebody else."""
        parsed_time = self.parse_natural_time(remind_time)
        natural_datetime = self.to_natural_day_and_time(parsed_time)
        if to_string:
            formatted_to_string = to_string
        else:
            formatted_to_string = ""
        formatted_reminder_text = \
            "%(reminder_recipient)s, %(from_handle)s asked me to remind you%(to_string)s %(reminder_text)s" % {
                "reminder_recipient": reminder_recipient,
                "from_handle": message.sender.mention_handle,
                "reminder_text": reminder_text,
                "to_string": formatted_to_string,
            }

        self.schedule_say(formatted_reminder_text, parsed_time, message=message, notify=True)
        self.say("%(reminder_text)s %(natural_datetime)s. Got it." % locals(), message=message)
