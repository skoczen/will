import pypco
import datetime
import os
from plugins.pco import msg_attachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

attachment_list = []


def get(name):
    # get the last attended date of a person to any service by name
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
    nickname = ""
    pco_id = x.id
    try:
        check_ins = pco.check_ins.people.list_by_url(
            'https://api.planningcenteronline.com/check_ins/v2/people/' + pco_id + '/check_ins?order=-created_at')
        first_record = True
        for a in check_ins:
            while first_record:
                last_checkin = a.created_at
                last_checkin = datetime.datetime.strptime(last_checkin, '%Y-%m-%dT%H:%M:%SZ')
                last_checkin = last_checkin.strftime('%B %d, %Y')
                last_checkin = str(last_checkin)
                first_record = False
                if x.nickname:
                    nickname = '"' + x.nickname + '"'
                else:
                    nickname = ""
                pco_id = "AC" + pco_id
                if nickname:
                    msg = " ".join(["The last time", x.first_name, nickname, x.last_name, "checked in was:\n" +
                                    last_checkin])
                else:
                    msg = " ".join(["The last time", x.first_name, x.last_name, "checked in was:\n" + last_checkin])
                url = "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])
                attachment_list.append(msg_attachment.SlackAttachment(fallback=msg, pco="check_ins", text=msg,
                                                                      button_text="Open in Check-ins", button_url=url))

    except:
        pco_id = "AC" + pco_id
        if nickname:
            msg = " ".join(["No check-ins found for:", x.first_name, nickname, x.last_name])
        else:
            msg = " ".join(["No check-ins found for:", x.first_name, x.last_name])
        url = "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])
        attachment_list.append(msg_attachment.SlackAttachment(fallback=msg, pco="check_ins", text=msg,
                                                              button_text="Open in Check-ins", button_url=url))
    finally:
        return


if __name__ == '__main__':
    name = "John"
    print("Getting attendance for ", name)
    x = get(name)
    for i in x:
        print(i.slack())
