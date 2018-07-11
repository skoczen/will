from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will.plugins.pco import birthday, address, phone_numbers, attendance, msg_attachment

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable


class PcoPeoplePlugin(WillPlugin):

    @respond_to("(?:when was )?(last time |!checkin |attended |when did )"
                "(?P<pco_name>.*?(?=(?:\'|\?|\.|and|was|attended|checked|check|attend)|$))", acl=["pastors", "staff"])
    def pco_checkin_lookup(self, message, pco_name):
        self.reply("Let me check.")
        attachment = attendance.get(pco_name)
        if attachment:
            self.reply("Looks like: ", message=message, attachments=attachment)
        else:
            attachment = msg_attachment.SlackAttachment(text="Sorry I don't have any records for " + pco_name + "'s last checkin.",
                                                        button_text="Open People",
                                                        button_url="https://people.planningcenteronline.com/people?q=" + pco_name.replace(
                                                            " ", "%20"))
            self.reply("", message=message, attachments=attachment.slack())


if __name__ == '__main__':
    name = "John"
    print("Checking attendance for", name)
    for x in attendance.get(name):
        print(x.txt)