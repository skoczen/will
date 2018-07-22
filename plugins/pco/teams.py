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

def get_team_assignments(team):
    msg = ""
    if team:
            for t in pco.services.teams.list(where={'name': team}, include='people'):
                service = t.rel.service_type.get().id
                team_id = t.id

                for member in t.rel.people.list():
                    print(pco.services.people.get(member.id).first_name)
                    print(pco.services.people.get(member.id).last_name)
                    for plan_people in member.rel.plan_people.list():
                        print(plan_people.team_position_name)

    else:
        print("No team given")

    return



if __name__ == '__main__':
    team = 'Band'
    # print("Getting a team:")
    # for x in get(team):
    #     print(x.slack())
    print("Getting Team Assignments:")
    get_team_assignments(team)
