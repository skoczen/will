import pypco
import os
from will.plugins.pco import msg_attachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    gotaddress = ""
    attachment = []
    try:
        fl_name = {'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        attachment_list = []
        for x in pco.people.people.list(where=fl_name):
            print("Your mom loves ", x.name)
            try:
                print("in the try with ", x.name)
                pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
                for address in x.rel.addresses.list():
                    print("in the for with ",x.name)
                    address = {'name': x.name, 'location': address.location, 'street': address.street,
                               'city': address.city, 'state': address.state, 'zip': address.zip}
                    gotaddress = "\n".join([gotaddress, address["name" ""], address["location" ""],
                                            address["street" ""],
                                            " ".join([address["city" ""], address["state" ""], address["zip" ""]])])
                    googleaddress = "+".join(["https://www.google.com/maps/dir/?api=1&destination=",
                                              address["street" ""].replace(" ", "+"),
                                              address["city" ""].replace(" ", "+"),
                                              address["state" ""].replace(" ", "+"), address["zip" ""]])
                    print(gotaddress)
                    attachment = (msg_attachment.SlackAttachment(pco="people", text=gotaddress,
                                                                 button_text="Open in People", button_url=pcoaddress))
                    attachment.add_button(text="Google Maps", url=googleaddress)
                    attachment_list.append(attachment)
                    address = ""
                    gotaddress = ""
            except TypeError:
                print("your mom sucks")
                attachment_list.append(msg_attachment.SlackAttachment(fallback="Couldn't find address.",
                                                                      text=" ".join(
                                                                          ["There's a problem with the address for", x.name + ".",
                                                                           "Maybe you can fix it?"]),
                                                                      button_url=pcoaddress,
                                                                      button_text="Open in People", pco="people"))
        return attachment_list


if __name__ == '__main__':
    name = "John"
    print("Getting address for ", name)
    for y in get(name):
        print(y.slack())
