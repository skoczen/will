import pypco
import os
from will.plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    # Get the birthday of person(s) and return a formated string ready to send back.
    bdays = ""
    attachment_list = []
    try:
        fl_name ={'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        for x in pco.people.people.list(where=fl_name):
            pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
            print(x.name,x.birthdate)
            if x.birthdate is None:
                attachment_list.append(msg_attachment.SlackAttachment(fallback=pcoaddress,
                                                                      text=" ".join(["I can't find a birthday for ", x.name,
                                                                                     "Maybe you could add it?"]),
                                                                      button_url=pcoaddress, button_text="Open in People", pco="people"))
            else:
                bdays = {'name': x.name, 'birthday': x.birthdate}
                attachment_list.append(msg_attachment.SlackAttachment(
                    fallback=pcoaddress,
                    text="\n".join([bdays["name" ""], bdays["birthday" ""]]),
                    button_url=pcoaddress,button_text="Open in People", pco="people"))
                bdays = ""

        return attachment_list


if __name__ == '__main__':
    name = "John"
    print("Getting birthdays for ", name)
    for x in get(name):
        print(x.slack())
