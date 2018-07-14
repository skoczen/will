import pypco
import os
from will.plugins.pco import msg_attachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


# This checks to see if the credentials {"name": "", "email": ""} have access to the app
# Apps: services, people, accounts, resources, check-ins, registrations, giving
# You should call this before accessing sensitive Planning Center Information
def get(credentials, app):
    fl_name = {'first_name': credentials['name' ''].split()[0], 'last_name': credentials['name' ''].split()[1]}
    app = app.lower().lstrip()
    for x in pco.people.people.list(where=fl_name):
        for email in x.rel.emails.list():
            if credentials['email' ''] in email.address:
                for apps in x.rel.apps.list():
                    if app in apps.name.lower():
                        return True

    return False


def get_apps(credentials):
    fl_name = {'first_name': credentials['name' ''].split()[0], 'last_name': credentials['name' ''].split()[1]}
    app_list = ""
    for x in pco.people.people.list(where=fl_name):
        pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
        for apps in x.rel.apps.list():
            app_list += "\n" + apps.name
    attachment = msg_attachment.SlackAttachment(fallback=app_list, text=app_list,
                                                button_text="Open in People", button_url=pcoaddress)
    return attachment


if __name__ == '__main__':
    name = "Ron Hudson"
    email = "pastorron@yourcbcfamily.org"
    app = "people"
    credentials = {"name": name, "email": email}
    print(get(credentials, app))
    # info = get_apps(credentials)
    # print(info.txt())
