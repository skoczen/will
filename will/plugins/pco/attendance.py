import pypco
import datetime
import os
from sys import platform

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(name):
    # get the last attended date of a person to any service by name
    last_checkin = ""
    attachment = []
    try:
        for x in pco.people.people.list(where={'first_name': name.split()[0], 'last_name': name.split()[1]}):
            pco_id = x.id
            check_ins = pco.check_ins.people.list_by_url(
                'https://api.planningcenteronline.com/check_ins/v2/people/' + pco_id + '/check_ins?order=-created_at')
            first_record = True
            time_stamp = datetime.datetime
            for a in check_ins:
                while first_record:
                    last_checkin = a.created_at
                    last_checkin = datetime.datetime.strptime(last_checkin, '%Y-%m-%dT%H:%M:%SZ')
                    if platform == "linux" or platform == "linux2":
                        last_checkin = last_checkin.strftime('%B %-d, %Y')  # linux
                    elif platform == "win32":
                        last_checkin = last_checkin.strftime('%B %#d, %Y')  # windows
                    last_checkin = str(last_checkin)
                    first_record = False
            pco_id = "AC" + pco_id
            attachment += [
                {
                    "fallback": "",
                    "color": "#876096",
                    "text": (" ".join(["The last time", x.first_name,x.last_name, "checked in was: \n", last_checkin])),
                    "actions": [
                        {
                            "color": "#3B80C6",
                            "type": "button",
                            "text": "Open in Check-ins",
                            "url": (
                                "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])),
                        }
                    ],
                    "footer": "Planning Center Online API",
                    "footer_icon": "https://d20n8yffv74pqs.cloudfront.net/assets/check-ins/favicon-128-4ba5f33023f9771353564e67c6e1e049b0e7eea2f0c881c58432a3adc93a44ab.png"

                }
            ]
            last_checkin = ""

    except IndexError:
        for x in pco.people.people.list(where={'first_name': name.split()[0]}):
            pco_id = x.id
            check_ins = pco.check_ins.people.list_by_url(
                'https://api.planningcenteronline.com/check_ins/v2/people/' + pco_id + '/check_ins?order=-created_at')
            first_record = True
            for a in check_ins:
                while first_record:
                    last_checkin = a.created_at
                    last_checkin = datetime.datetime.strptime(last_checkin, '%Y-%m-%dT%H:%M:%SZ')
                    if platform == "linux" or platform == "linux2":
                        last_checkin = last_checkin.strftime('%B %-d, %Y')  # linux
                    elif platform == "win32":
                        last_checkin = last_checkin.strftime('%B %#d, %Y')  # windows
                    last_checkin = str(last_checkin)
                    first_record = False
            pco_id = "AC" + pco_id
            attachment += [
                {
                    "fallback": "",
                    "color": "#876096",
                    "text": (" ".join(["The last time", x.first_name,x.last_name,"checked in was: \n", last_checkin])),
                    "actions": [
                        {
                            "color": "#3B80C6",
                            "type": "button",
                            "text": "Open in Check-ins",
                            "url": (
                                "/".join(["https://check-ins.planningcenteronline.com/people", pco_id, "activity"])),
                        }
                    ],
                    "footer": "Planning Center Online API",
                    "footer_icon": "https://d20n8yffv74pqs.cloudfront.net/assets/check-ins/favicon-128-4ba5f33023f9771353564e67c6e1e049b0e7eea2f0c881c58432a3adc93a44ab.png"

                }
            ]
            last_checkin = ""
    finally:
        return attachment


if __name__ == '__main__':
    name = "John"
    print("Getting attendance for ", name)
    print(get(name))
