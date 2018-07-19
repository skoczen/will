import pypco
import os
from plugins.pco import msg_attachment


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])
attachment_list = []


def get(team):
    team = team.strip()
    print("Looking up the team: ", team)
    msg = ""
    if team:
            for t in pco.services.teams.list(where={'name': team}, include='people'):
                service = t.rel.service_type.get().id
                team_id = t.id
                msg += "*" + pco.services.service_types.get(service).name
                msg += " " + t.name + ":*"
                for id_number in t.rel.people.list():
                    msg += "\n" + " ".join([pco.services.people.get(id_number.id).first_name,
                                       pco.services.people.get(id_number.id).last_name])
                attachment_list.append(msg_attachment.SlackAttachment(fallback=msg, pco='services',
                                                                      text=msg, button_text="Open in Services",
                                                                      button_url="/".join(["https://services."
                                                                                           "planningcenteronline.com/"
                                                                                           "service_types",
                                                                                           service, "teams", team_id,
                                                                                           "positions"])))
                msg = ""
    else:
        print("else")
        msg = "*Planning Center Services Teams:*"
        for team in pco.services.teams.list():

            msg += "\n" + team.name
        attachment_list.append(msg_attachment.SlackAttachment(fallback=msg, pco='services',
                                                              text=msg, button_text="Open in Services",
                                                              button_url="https://services.planning"
                                                                         "centeronline.com/teams"))

    # print("msg before assigning to attachment: ", msg)
    return attachment_list


if __name__ == '__main__':
    for x in get('oasis team'):
        print(x.slack())
