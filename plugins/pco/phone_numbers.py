import pypco
import os
from plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

attachment_list = []


def get(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    phone_numbers = ""
    try:
        fl_name = {'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        for x in pco.people.people.list(where=fl_name):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for pnumber in x.rel.phone_numbers.list():
                if pnumber.number is None:
                    attachment_list.append(msg_attachment.SlackAttachment(fallback=pcoaddress,
                                                                          text=" ".join(
                                                                              ["I can't find a number for ", x.name,
                                                                               "Maybe you could add it?"]),
                                                                          button_url=pcoaddress,
                                                                          button_text="Open in People", pco="people"))

                number = {'name': x.name, 'phone': pnumber.number}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([phone_numbers, number["name" ""], number["phone" ""]]),
                    button_url=pcoaddress, button_text="Open in People", pco="people"))
        get_nickname(name)
        return attachment_list


def get_nickname(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    phone_numbers = ""
    fl_name = {'nickname': name}
    for x in pco.people.people.list(where=fl_name):
        pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
        for pnumber in x.rel.phone_numbers.list():
            if pnumber.number is None:
                attachment_list.append(msg_attachment.SlackAttachment(fallback=pcoaddress,
                                                                      text=" ".join(
                                                                          ["I can't find a number for ", x.name,
                                                                           "Maybe you could add it?"]),
                                                                      button_url=pcoaddress,
                                                                      button_text="Open in People", pco="people"))

            number = {'name': " ".join([x.first_name, '"' + x.nickname + '"', x.last_name]),
                      'phone': pnumber.number}
            attachment_list.append(msg_attachment.SlackAttachment(
                fallback=pcoaddress,
                text="\n".join([phone_numbers, number["name" ""], number["phone" ""]]),
                button_url=pcoaddress, button_text="Open in People", pco="people"))
        return


if __name__ == '__main__':
    name = "John"
    print("Getting phone numbers for ", name)
    x = get(name)
    for i in x:
        print(i.slack())
