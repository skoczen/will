import pypco
import os
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
import datetime
import parsedatetime
import os
from sys import platform

# You need to put your Personal access token application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get_phone_numbers(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    phone_numbers = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            for pnumber in x.rel.phone_numbers.list():
                pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
                number = {'name': x.name, 'phone': pnumber.number}
                phone_numbers = "\n".join([phone_numbers, number["name" ""], number["phone" ""]])
                attachment += [
                    {
                        "fallback": phone_numbers,
                        "color": "#007AB8",
                        "text": phone_numbers,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Open in PCO",
                                "url": pcoaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                phone_numbers = ""
                pcoaddress = ""

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for pnumber in x.rel.phone_numbers.list():
                number = {'name': x.name, 'phone': pnumber.number}
                phone_numbers = "\n".join([phone_numbers, number["name" ""], number["phone" ""]])
                attachment += [
                    {
                        "fallback": phone_numbers,
                        "color": "#007AB8",
                        "text": phone_numbers,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Open in PCO",
                                "url": pcoaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                phone_numbers = ""
                pcoaddress = ""
    finally:
        return attachment


def get_birthday(name):
    # Get the birthday of person(s) and return a formated string ready to send back.
    bdays = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            if x.birthdate is None:
                bdays = bdays + " " + " ".join([x.name, "needs birthday added to pco."])

            else:
                bdays = bdays + " " + " ".join([x.name, x.birthdate])
                attachment += [
                    {
                        "fallback": bdays,
                        "color": "#007AB8",
                        "text": bdays,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Open in PCO",
                                "url": pcoaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                bdays = ""
                pcoaddress = ""

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            if x.birthdate is None:
                bdays = bdays + " " + " ".join([x.name, "needs birthday added to pco."])
            else:
                bdays = bdays + " " + " ".join([x.name, x.birthdate])
                attachment += [
                    {
                        "fallback": bdays,
                        "color": "#007AB8",
                        "text": bdays,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Open in PCO",
                                "url": pcoaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                bdays = ""
                pcoaddress = ""


    finally:
        return attachment


def get_address(name):
    gotaddress = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            for address in x.rel.addresses.list():
                address = {'name': x.name, 'location': address.location, 'street': address.street,
                           'city': address.city, 'state': address.state, 'zip': address.zip}
                gotaddress = "\n".join([gotaddress, address["name" ""], address["location" ""],
                                          address["street" ""], " ".join([address["city" ""], address["state" ""],
                                                                          address["zip" ""]])])
                googleaddress = "+".join(["https://www.google.com/maps/dir/?api=1&destination=",
                                          address["street" ""].replace(" ", "+"), address["city" ""].replace(" ", "+"),
                                          address["state" ""].replace(" ", "+"), address["zip" ""]])
                attachment += [
                    {
                        "fallback": gotaddress,
                        "color": "#007AB8",
                        "text": gotaddress,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Google Map",
                                "url": googleaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                gotaddress = ""
                googleaddress = ""

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            for address in x.rel.addresses.list():
                address = {'name': x.name, 'location': address.location, 'street': address.street,
                           'city': address.city, 'state': address.state, 'zip': address.zip}
                gotaddress = "\n".join([gotaddress, address["name" ""], address["location" ""],
                                          address["street" ""], " ".join([address["city" ""], address["state" ""],
                                                                          address["zip" ""]])])
                googleaddress = "+".join(["https://www.google.com/maps/dir/?api=1&destination=",
                                          address["street" ""].replace(" ", "+"), address["city" ""].replace(" ", "+"),
                                          address["state" ""].replace(" ", "+"), address["zip" ""]])
                # Build Slack style 'attachment'
                attachment += [
                    {
                        "fallback": gotaddress,
                        "color": "#007AB8",
                        "text": gotaddress,
                        "actions": [
                            {
                                "color": "#3B80C6",
                                "type": "button",
                                "text": "Google Map",
                                "url": googleaddress
                            }
                        ],
                        "footer": "Planning Center Online API",
                        "footer_icon": "https://d1pz3w4vu41eda.cloudfront.net/assets/people/favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"

                    }
                ]
                gotaddress = ""
                googleaddress = ""

    finally:
        return attachment


def get_attendance(name):
    # get the last attended date of a person to any service by name
    last_checkin = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pco_id = x.id
            check_ins = pco.check_ins.people.list_by_url(
                'https://api.planningcenteronline.com/check_ins/v2/people/' + pco_id + '/check_ins?order=-created_at')
            first_record = True
            time_stamp = datetime.datetime
            for a in check_ins:
                while first_record:
                    last_checkin = a.created_at
                    last_checkin = datetime.datetime.strptime(last_checkin, '%Y-%m-%dT%H:%M:%SZ')
                    if platform == "linux" or platform == "linux2":
                        last_checkin = last_checkin.strftime('%B %-d, %Y')  # linux
                    elif platform == "win32":
                        last_checkin = last_checkin.strftime('%B %#d, %Y')  # windows
                    last_checkin = str(last_checkin)
                    first_record = False
            pco_id = "AC" + pco_id
            attachment += [
                {
                    "fallback": "",
                    "color": "#876096",
                    "text": (" ".join(["The last time", x.first_name,x.last_name, "checked in was: ", last_checkin])),
                    "actions": [
                        {
                            "color": "#3B80C6",
                            "type": "button",
                            "text": "Open in PCO",
                            "url": (
                                "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])),
                        }
                    ],
                    "footer": "Planning Center Online API",
                    "footer_icon": "https://d20n8yffv74pqs.cloudfront.net/assets/check-ins/favicon-128-4ba5f33023f9771353564e67c6e1e049b0e7eea2f0c881c58432a3adc93a44ab.png"

                }
            ]
            last_checkin = ""

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pco_id = x.id
            check_ins = pco.check_ins.people.list_by_url(
                'https://api.planningcenteronline.com/check_ins/v2/people/' + pco_id + '/check_ins?order=-created_at')
            first_record = True
            for a in check_ins:
                while first_record:
                    last_checkin = a.created_at
                    last_checkin = datetime.datetime.strptime(last_checkin, '%Y-%m-%dT%H:%M:%SZ')
                    if platform == "linux" or platform == "linux2":
                        last_checkin = last_checkin.strftime('%B %-d, %Y')  # linux
                    elif platform == "win32":
                        last_checkin = last_checkin.strftime('%B %#d, %Y')  # windows
                    last_checkin = str(last_checkin)
                    first_record = False

            attachment += [
                {
                    "fallback": "",
                    "color": "#876096",
                    "text": (" ".join(["The last time", x.first_name,x.last_name,"checked in was: ", last_checkin])),
                    "actions": [
                        {
                            "color": "#3B80C6",
                            "type": "button",
                            "text": "Open in PCO",
                            "url": (
                                "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])),
                        }
                    ],
                    "footer": "Planning Center Online API",
                    "footer_icon": "https://d20n8yffv74pqs.cloudfront.net/assets/check-ins/favicon-128-4ba5f33023f9771353564e67c6e1e049b0e7eea2f0c881c58432a3adc93a44ab.png"

                }
            ]
            last_checkin = ""
    finally:
        return attachment

class PcoPeoplePlugin(WillPlugin):

    @hear("(?:do you |find |got |a |need to |can somebody )?(number for |!number |!phone |call )"
          "(?P<pco_name>.*?(?=(?:\'|\?|\.|and)|$))", acl=["pastors", "staff"])
    def pco_phone_lookup(self, message, pco_name):
        print("got phone request")
        self.reply("I might have that number I'll check.")
        numbers = ""
        numbers = get_phone_numbers(pco_name)
        if numbers:
            self.reply("Here you go!", message=message, attachments=numbers)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s number.")

    @hear("(?:do you |find |got |a )?(birthday for |!birthday |!birth )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
          acl=["pastors", "staff"])
    def pco_birthday_lookup(self, message, pco_name):
        self.reply("I might have that birthdate.")
        bdays = get_birthday(pco_name)
        if bdays:
            self.reply("Happy Birthday!", message=message, attachments=bdays)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s birthdate.")

    @hear("(?:do you |find |got |a )?(address for |!address )(?P<pco_name>.*?(?=(?:\'|\?)|$))",
              acl=["pastors", "staff"])
    def pco_address_lookup(self, message, pco_name):
        self.reply("I might have that address.")
        address = get_address(pco_name)
        if address:
            self.reply("Found it!", message=message, attachments=address)
        else:
            self.reply("Sorry I don't have " + pco_name + "'s address. You should add it to Planning Center.")

    @hear("(when was |was )?(last time |!checkin |!attendance )(?P<pco_name>.*?(?=(?:\'|\?)|$|))(here last |was here)",
          acl=["pastors", "staff"])
    def pco_checkin_lookup(self, message, pco_name):
        self.reply("Let me check.")
        attendance = get_attendance(pco_name)
        if attendance:
            self.reply("Looks like: ", message=message, attachments=attendance)
        else:
            self.reply("Sorry I don't have any records for " + pco_name + "'s check-in's")

# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    print("Getting phone numbers for ", name)
    print(get_phone_numbers(name))
    print("Getting birthdays for ", name)
    print(get_birthday(name))
    print("Checking attendance for", name)
    print(get_attendance(name))