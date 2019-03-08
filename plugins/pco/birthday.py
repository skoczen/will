import pypco
import os
import datetime
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
        fl_name = fl_name = {'nickname': name}
        for x in pco.people.people.list(where=fl_name):
            build(x)

        return attachment_list


def build(x):
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


# This returns one attachment not a list.
def get_todays_birthdays():
    msg = "*Today's Birthdays!*\n"
    today = datetime.datetime.today().strftime('%m-%d')
    for x in pco.people.people.list():
        if today in str(x.birthdate)[5:] and x.status == 'active':
                msg += "%s\n" % x.name
    attachment = msg_attachment.SlackAttachment(fallback=msg, text=msg)
    return attachment


def announce_todays_birthdays(will, channel='announcements'):
    attachment = get_todays_birthdays()
    if attachment.txt() != "*Today's Birthdays!*\n":
        will.say("", attachments=attachment.slack(), channel=channel)
    else:
        print("Skipping birthday announcement because there are no birthdays today.")


if __name__ == '__main__':
    # name = "John"
    # print("Getting birthdays for ", name)
    # for x in get(name):
    #     print(x.slack())
    print("Getting today's birthdays")
    print(get_todays_birthdays().txt())
