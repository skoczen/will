import pypco
import os
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get_phone_numbers(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    phone_numbers = ""
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            for pnumber in x.rel.phone_numbers.list():
                number = {'name': x.name, 'phone': pnumber.number}
                # print("\n".join([number["name" ""], number["phone" ""]]))
                rrphone_numbers = "\n".join([phone_numbers, number["name" ""], number["phone" ""]])
    except Exception as e:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            for pnumber in x.rel.phone_numbers.list():
                number = {'name': x.name, 'phone': pnumber.number}
                # print("\n".join([number["name" ""], number["phone" ""]]))
                phone_numbers = "\n".join([phone_numbers, number["name" ""], number["phone" ""]])
    finally:
        return phone_numbers


def get_birthday(name):
    # Get the birthday of person(s) and return a formated string ready to send back.
    bdays = ""
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            # print(x.name)
            # print(x.birthdate)
            if x.birthdate is None:
                bdays = bdays + " " + " ".join([x.name, " needs birthday added to pco."])
            else:
                bdays = bdays + " " + " ".join([x.name, x.birthdate])

    # TODO make this a popper exception catcher
    except:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            # print(x.name)
            # print(x.birthdate)
            if x.birthdate is None:
                bdays = bdays + " " + " ".join([x.name, " needs birthday added to pco."])
            else:
                bdays = bdays + " " + " ".join([x.name, x.birthdate])

    finally:
        return bdays


class PcoPeoplePlugin(WillPlugin):

    @hear("(?:do you |find |got |a |need to |can somebody )?(number for |!number |!phone |call )"
          "(?P<pco_name>.*?(?=(?:\'|\?|\.)|$))", acl=["pastors", "staff"])
    def pco_phone_lookup(self, message, pco_name):
        # print("Sending phone number from pco")
        # print(pco_name)
        self.reply("I might have that number I'll check.")
        numbers = ""
        numbers = get_phone_numbers(pco_name)
        # print(numbers)
        if numbers is "":
            self.reply("Sorry I don't have " + pco_name + "'s number.")
        else:
            self.reply(numbers)

    @hear("(?:do you |find |got |a )?(birthday for |!birthday |!birth )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
          acl=["pastors", "staff"])
    def pco_birthday_lookup(self, message, pco_name):
        # print("Looking up birthday")
        self.reply("I might have that birthdate.")
        bdays = get_birthday(pco_name)
        if bdays is None:
            self.reply("Sorry I don't have " + pco_name + "'s birthdate.")

        self.reply(bdays)

# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    print("Getting phone numbers for 'John'")
    get_phone_numbers('John')
    print("Getting birthdays  for 'John'")
    get_birthday('John')
