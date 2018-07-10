from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will.plugins.pco import birthday, address, phone_numbers, attendance, emails, msg_attachment

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable


class PcoPeoplePlugin(WillPlugin):

    @respond_to("(?:do you |find |got |a |need to |can somebody )?(number for |!number |!phone |call )"
          "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))", acl=["pastors", "staff"])
    def pco_phone_lookup(self, message, pco_name):
        self.reply("I might have that number I'll look.")
        attachment = []
        for x in phone_numbers.get(pco_name):
            attachment += x.slack()
        if not attachment:
            attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a number for " + pco_name,
                                                        button_text="Open People",
                                                        button_url="https://people.planningcenteronline.com/people?q=" + pco_name.replace(" ", "%20"))
            print(attachment.slack())
            self.reply("", message=message, attachments=attachment.slack())
        else:
            self.reply("Here you go!", message=message, attachments=attachment)

    @respond_to("(?:do you |find |got |a )?(birthday for |!birthday |!birth )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
          acl=["pastors", "staff"])
    def pco_birthday_lookup(self, message, pco_name):
        self.reply("I might have that birthdate.")
        bdays = birthday.get(pco_name)
        if bdays:
            self.reply("Happy Birthday!", message=message, attachments=bdays)
        else:
            attachment = msg_attachment.SlackAttachment(text="Sorry I don't have a birthday for " + pco_name,
                                                        button_text="Open People",
                                                        button_url="https://people.planningcenteronline.com/people?q=" + pco_name.replace(
                                                            " ", "%20"))
            print(attachment.slack())
            self.reply("", message=message, attachments=attachment.slack())

    @respond_to("(?:do you |find |got |a )?(address for |!address )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
              acl=["pastors", "staff"])
    def pco_address_lookup(self, message, pco_name):
        self.reply("I might have that address.")
        attachment = address.get(pco_name)
        if attachment:
            self.reply("Found it!", message=message, attachments=attachment)
        else:
            attachment = msg_attachment.SlackAttachment(text="Sorry I don't have an address for " + pco_name,
                                                        button_text="Search People",
                                                        button_url="https://people.planningcenteronline.com/people?q=" + pco_name.replace(
                                                            " ", "%20"))
            print(attachment.slack())
            self.reply("", message=message, attachments=attachment.slack())

    @respond_to("(?:do you |find |got |a |need to |can somebody )?(email for |!email |email )"
                "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))", acl=["pastors", "staff"])
    def pco_email_lookup(self, message, pco_name):
        self.reply("I might have that email address. I'll look.")
        attachment = []
        for x in emails.get(pco_name):
            attachment += x.slack()
        if not attachment:
            attachment = msg_attachment.SlackAttachment(text="Sorry I don't have an email address for " + pco_name,
                                                        button_text="Search People",
                                                        button_url="https://people.planningcenteronline.com/people?q=" + pco_name.replace(
                                                            " ", "%20"))
            print(attachment.slack())
            self.reply("", message=message, attachments=attachment.slack())
        else:
            self.reply("Here you go!", message=message, attachments=attachment)


# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    # print("Getting phone numbers for ", name)
    # print(phone_numbers.get(name))
    # for x in phone_numbers.get(name):
    #     print(x.slack())
    # print("Getting address for ", name)
    # print(address.get(name))
    print("Getting birthdays for ", name)
    print(birthday.get(name))

