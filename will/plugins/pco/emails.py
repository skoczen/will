import pypco
import os
from will.plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    info = ""
    attachment_list = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for email in x.rel.emails.list():
                e_mail = {'name': x.name, 'email': email.address}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([info, e_mail["name" ""], e_mail["email" ""]]),
                    button_url=pcoaddress, button_text="Open in People", pco="people"))

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for email in x.rel.emails.list():
                e_mail = {'name': x.name, 'email': email.address}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([info, e_mail["name" ""], e_mail["email" ""]]),
                    button_url=pcoaddress, button_text="Open in People", pco="people"))
    finally:
        return attachment_list


if __name__ == '__main__':
    name = "John"
    print("Getting emails for ", name)
    x = get(name)
    for i in x:
        print(i.txt())
