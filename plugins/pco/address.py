import pypco
import os
from plugins.pco import msg_attachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])
attachment_list = []


def get(name):
    try:
        fl_name = {'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        for x in pco.people.people.list(where=fl_name):
            build(x)
        fl_name = {'nickname': name}
        for x in pco.people.people.list(where=fl_name):
            build(x)

        return attachment_list

def build(x):
    gotaddress = ""
    address = ""
    pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
    if x.nickname:
        name = " ".join([x.first_name, '"' + x.nickname + '"', x.last_name])
    else:
        name = x.name

    try:
        for address in x.rel.addresses.list():
            address = {'name': name, 'location': address.location, 'street': address.street,
                       'city': address.city, 'state': address.state, 'zip': address.zip}
            gotaddress = "\n".join([gotaddress, address["name" ""], address["location" ""],
                                    address["street" ""],
                                    " ".join([address["city" ""], address["state" ""], address["zip" ""]])])
            googleaddress = "+".join(["https://www.google.com/maps/dir/?api=1&destination=",
                                      address["street" ""].replace(" ", "+"),
                                      address["city" ""].replace(" ", "+"),
                                      address["state" ""].replace(" ", "+"), address["zip" ""]])
            attachment = (msg_attachment.SlackAttachment(pco="people", text=gotaddress,
                                                         button_text="Open in People", button_url=pcoaddress))
            attachment.add_button(text="Google Maps", url=googleaddress)
            attachment_list.append(attachment)
    except TypeError:
        attachment_list.append(msg_attachment.SlackAttachment(pco="people", text="There's a problem with " + name +
                                                                                 "'s address.",
                                                              button_text="Open in People", button_url=pcoaddress))

    finally:
        return


if __name__ == '__main__':
    name = "John"
    print("Getting address for ", name)
    for y in get(name):
        print(y.slack())
