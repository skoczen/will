import pypco
import os
from sys import platform


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
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


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    print("Getting phone numbers for ", name)
    print(get(name))
