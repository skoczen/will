from will.plugin import WillPlugin
from will.decorators import hear
from will.plugins.pco import birthday, address, phone_numbers, attendance

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable


class PcoPeoplePlugin(WillPlugin):

    @hear("(?:do you |find |got |a |need to |can somebody )?(number for |!number |!phone |call )"
          "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))", acl=["pastors", "staff"])
    def pco_phone_lookup(self, message, pco_name):
        print("got phone request")
        self.reply("I might have that number I'll check.")
        numbers = phone_numbers.get(pco_name)
        if numbers:
            self.reply("Here you go!", message=message, attachments=numbers)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s number.")

    @hear("(?:do you |find |got |a )?(birthday for |!birthday |!birth )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
          acl=["pastors", "staff"])
    def pco_birthday_lookup(self, message, pco_name):
        self.reply("I might have that birthdate.")
        bdays = birthday.get(pco_name)
        if bdays:
            self.reply("Happy Birthday!", message=message, attachments=bdays)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s birthday.")

    @hear("(?:do you |find |got |a )?(address for |!address )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
              acl=["pastors", "staff"])
    def pco_address_lookup(self, message, pco_name):
        self.reply("I might have that address.")
        attachment = address.get(pco_name)
        if attachment:
            self.reply("Found it!", message=message, attachments=attachment)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s address. You should add it to Planning Center.")

    @hear("(when was )?(last time |!checkin |!attendance |was |the last time )(?P<pco_name>.*?(?=(?:\'|\?)|$))", #(?: here sunday?|here last |was here|$|\?)
          acl=["pastors", "staff"])
    def pco_checkin_lookup(self, message, pco_name):
        self.reply("Let me check.")
        attachment = attendance.get(pco_name)
        if attachment:
            self.reply("Looks like: ", message=message, attachments=attachment)
        else:
            self.reply("Sorry I don't have any records for " + pco_name + "'s check-in's")

# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    print("Getting phone numbers for ", name)
    print(phone_numbers.get(name))
    print("Getting address for ", name)
    print(address.get(name))
    print("Getting birthdays for ", name)
    print(birthday.get(name))
    print("Checking attendance for", name)
    print(attendance.get(name))
