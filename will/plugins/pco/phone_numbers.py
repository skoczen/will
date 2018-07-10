import pypco
import os
from will.plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    phone_numbers = ""
    attachment_list = []

    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for pnumber in x.rel.phone_numbers.list():
                number = {'name': x.name, 'phone': pnumber.number}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([phone_numbers, number["name" ""], number["phone" ""]]),
                    button_url=pcoaddress,button_text="Open in People", pco="people"))

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            for pnumber in x.rel.phone_numbers.list():
                number = {'name': x.name, 'phone': pnumber.number}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([phone_numbers, number["name" ""], number["phone" ""]]),
                    button_url=pcoaddress,button_text="Open in People", pco="people"))

    finally:
        return attachment_list


if __name__ == '__main__':
    name = "John"
    print("Getting phone numbers for ", name)
    x = get(name)
    for i in x:
        print(i.slack())
