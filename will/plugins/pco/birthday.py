import pypco
import os


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    # Get the birthday of person(s) and return a formated string ready to send back.
    bdays = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            if x.birthdate is None:
                bdays = bdays + " " + " ".join([x.name, "needs birthday added to pco.\n"])

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
                bdays = bdays + " " + " ".join([x.name, "needs birthday added to pco.\n"])
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


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    print("Getting birthdays for ", name)
    print(get(name))
