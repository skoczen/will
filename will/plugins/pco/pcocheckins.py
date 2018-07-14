from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will.plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

app = "check-ins"


class PcoPeoplePlugin(WillPlugin):

    @respond_to("(?:when was )?(last time |!checkin |attended |when did )"
                "(?P<pco_name>.*?(?=(?:\'|\?|\.|and|was|attended|checked|check|attend)|$))")
    def pco_checkin_lookup(self, message, pco_name):
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            print("checkin request")
            self.reply("Let me check.")
            attachment = []
            attachment_txt = ""
            for x in checkins.get(pco_name):
                attachment += x.slack()
                attachment_txt += x.txt()
            if not attachment:
                attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a Check-in for " + pco_name,
                                                            pco="check_ins",
                                                            button_text="Search Check-ins",
                                                            button_url="https://check-ins."
                                                                       "planningcenteronline.com/people?q="
                                                                       + pco_name.replace(" ", "%20"))
                self.reply("", message=message, attachments=attachment.slack())
            else:
                self.reply("Here you go!", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the Check-ins App. "
                       "Please contact your administrator.")


if __name__ == '__main__':
    name = "John"
    print("Checking attendance for", name)
    for x in checkins.get(name):
        print(x.txt())
