from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import msg_attachment, authenticate, giving_report
from will.mixins.slackwhitelist import wl_chan_id
import logging

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

app = "giving"


class PcoGivingPlugin(WillPlugin):

    @respond_to("(?:do you |find |got |a |need to |can somebody )?(giving since |!giving |!donations )"
                "(?P<pco_date>.*?(?=(?:\'|\?|\.|and)|$))")
    def pco_giving_report(self, message, pco_date):
        """!giving | "giving since" (date): gives you a breakdown of giving since the date you specify."""
        if authenticate.check_name(message):
            if authenticate.get(message, app):
                    self.reply("Doing the math. This could take a few minutes.")
                    attachment = []
                    for x in giving_report.get_giving(pco_date):
                        attachment += x.slack()
                    if not attachment:
                        attachment = msg_attachment.\
                            SlackAttachment(text="Sorry something went wrong.",
                                            button_text="Search People",
                                            button_url="https://giving.planningcenteronline.com/"
                                                       "donations?period=last_7_days")
                        print(attachment.slack())
                        self.say("", message=message, attachments=attachment.slack())
                    else:
                        self.say("Here you go!", message=message, attachments=attachment, channel=wl_chan_id(self))
            else:
                self.say("Sorry but you don't have access to the Giving App. "
                         "Please contact your administrator.", channel=wl_chan_id(self))
        else:
            self.say('I could not authenticate you. Please make sure your "Full name" '
                     'is in your Slack profile and matches your Planning Center Profile.', channel=wl_chan_id(self))
