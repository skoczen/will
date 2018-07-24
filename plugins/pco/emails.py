import pypco
import os
from plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])
attachment_list = []


def get(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    try:
        fl_name = {'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        for x in pco.people.people.list(where=fl_name):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for email in x.rel.emails.list():
                e_mail = {'name': x.name, 'email': email.address}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([e_mail["name" ""], e_mail["email" ""]]),
                    button_url=pcoaddress, button_text="Open in People", pco="people"))
        get_nickname(name)
        return attachment_list


def get_nickname(name):
    fl_name = {'nickname': name}
    for x in pco.people.people.list(where=fl_name):
        pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
        for email in x.rel.emails.list():
            e_mail = {'name': " ".join([x.first_name, '"' + x.nickname + '"', x.last_name]),
                      'email': email.address}
            attachment_list.append(msg_attachment.SlackAttachment(
                fallback=pcoaddress,
                text="\n".join([e_mail["name" ""], e_mail["email" ""]]),
                button_url=pcoaddress, button_text="Open in People", pco="people"))
            email = {}
    return


if __name__ == '__main__':
    name = "John"
    print("Getting emails for ", name)
    x = get(name)
    for i in x:
        print(i.txt())
