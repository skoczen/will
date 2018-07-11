import pypco
import os
from will.plugins.pco import msg_attachment


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
        fl_name = fl_name = {'nickname': name}
        for x in pco.people.people.list(where=fl_name):
            build(x)

        return attachment_list

def build(x):
    nickname = ""
    bdays = {}
    pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
    if x.birthdate is None:
        return
    else:
        if x.nickname:
            nickname = '"' + x.nickname + '"'
        else:
            nickname = ""
        msg = " ".join([x.first_name, nickname, x.last_name, "\n" + x.birthdate])
        attachment_list.append(msg_attachment.SlackAttachment(
            fallback=pcoaddress,
            text=msg,
            button_url=pcoaddress, button_text="Open in People", pco="people"))
        return


if __name__ == '__main__':
    name = "John"
    print("Getting birthdays for ", name)
    for x in get(name):
        print(x.slack())
