from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, emails, msg_attachment, authenticate

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

app = "people"


class PcoPeoplePlugin(WillPlugin):

    @respond_to("(?:do you |find |got |a |need to |can somebody )?(number for |!number |!phone |call )"
                "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))")
    def pco_phone_lookup(self, message, pco_name):
        """!phone | "number for" (name): tells you the phone number of a certain user"""
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            self.reply("I might have that number I'll look.")
            attachment = []
            for x in phone_numbers.get(pco_name):
                attachment += x.slack()
            if not attachment:
                attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a number for " + pco_name,
                                                            button_text="Search People",
                                                            button_url="https://people.planningcenteronline.com/"
                                                                       "people?q=" + pco_name.replace(" ", "%20"))
                print(attachment.slack())
                self.reply("", message=message, attachments=attachment.slack())
            else:
                self.reply("Here you go!", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the People App. "
                       "Please contact your administrator.")

    @respond_to("(?:do you |find |got |a )?(birthday for |!birthday |!birth )(?P<pco_name>.*?(?=(?:\'|\?)|$))")
    def pco_birthday_lookup(self, message, pco_name):
        """!birthday | "birthday for" (name): tells you the birthday of a certain user"""
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            self.reply("I might have that birthday I'll look.")
            attachment = []
            for x in birthday.get(pco_name):
                attachment += x.slack()
            if not attachment:
                attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a birthday for " + pco_name,
                                                            button_text="Search People",
                                                            button_url="https://people.planningcenteronline.com/"
                                                                       "people?q=" + pco_name.replace(" ", "%20"))
                print(attachment.slack())
                self.reply("", message=message, attachments=attachment.slack())
            else:
                self.reply("Here you go!", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the People App. "
                       "Please contact your administrator.")

    @respond_to("(?:do you |find |got |a )?(address for |!address )(?P<pco_name>.*?(?=(?:\'|\?)|$))")
    def pco_address_lookup(self, message, pco_name):
         """!address | "address for" (name): tells you the street address of a certain user"""
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            self.reply("I might have that address.")
            attachment = []
            for x in address.get(pco_name):
                attachment += x.slack()
            if not attachment:
                attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a address for " + pco_name,
                                                            pco="people",
                                                            button_text="Search People",
                                                            button_url="https://people.planningcenteronline.com/"
                                                                       "people?q=" + pco_name.replace(" ", "%20"))
                print(attachment.slack())
                self.reply("", message=message, attachments=attachment.slack())
            else:
                self.reply("Here you go!", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the People App. "
                       "Please contact your administrator.")

    @respond_to("(?:do you |find |got |a |need to |can somebody )?(email for |!email |email )"
                "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))")
    def pco_email_lookup(self, message, pco_name):
        """!email | "email for" (name): tells you the email address of a certain user"""
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        if authenticate.get(credentials, app):
            self.reply("I might have that email address. I'll look.")
            attachment = []
            for x in emails.get(pco_name):
                attachment += x.slack()
            if not attachment:
                attachment = msg_attachment.SlackAttachment(text="Sorry I don't have an email address for " + pco_name,
                                                            button_text="Search People",
                                                            button_url="https://people.planningcenteronline.com/"
                                                                       "people?q=" + pco_name.replace(" ", "%20"))
                print(attachment.slack())
                self.reply("", message=message, attachments=attachment.slack())
            else:
                self.reply("Here you go!", message=message, attachments=attachment)
        else:
            self.reply("Sorry but you don't have access to the People App. "
                       "Please contact your administrator.")


# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    name = "John"
    print("Getting phone numbers for ", name)
    for x in phone_numbers.get(name):
        print(x.txt())
    print("Getting address for ", name)
    for x in address.get(name):
        print(x.txt())
    print("Getting birthdays for ", name)
    for x in birthday.get(name):
        print(x.txt())
