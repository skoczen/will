import pypco
import os

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
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


if __name__ == '__main__':
    name = "John"
    date = "sunday"
    print("Getting address for ", name)
    print(get(name))
