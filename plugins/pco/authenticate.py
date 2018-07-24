import pypco
import os
from plugins.pco import msg_attachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


# This checks to see if the credentials {"name": "", "email": ""} have access to the app
# Apps: services, people, accounts, resources, check-ins, registrations, giving
# You should call this before accessing sensitive Planning Center Information
def get(message, app):
    try:
        fl_name = {'first_name': message.sender['source']['real_name'].split()[0],
                   'last_name': message.sender['source']['real_name'].split()[1]}
        app = app.lower().strip()
        for x in pco.people.people.list(where=fl_name):
            for email in x.rel.emails.list():
                if message.sender['source']['email'] in email.address:
                    for apps in x.rel.apps.list():
                        if app in apps.name.lower():
                            return True
                            print("TRUE")
        return False
    except IndexError:
        return False


def check_name(message):
    print("Checking Slack name for First Last name:")
    print(message.sender['source']['real_name'])
    try:
        fl_name = (message.sender['source']['real_name'].split()[0], message.sender['source']['real_name'].split()[1])
        print(fl_name)
    except IndexError:
        print(message.sender['source']['real_name'])
        return False
    return True


def get_apps(message):
    fl_name = {'first_name': message.sender['source']['real_name'].split()[0],
               'last_name': message.sender['source']['real_name'].split()[1]}
    app_list = ""
    pcoaddress = ""
    for x in pco.people.people.list(where=fl_name):
        pcoaddress = "https://people.planningcenteronline.com/people/" + x.id
        for apps in x.rel.apps.list():
            app_list += "\n" + apps.name
    print(app_list)
    if app_list is "":
        print("else")
        pcoaddress = ("https://people.planningcenteronline.com/people?q=" + "%20".join([fl_name['first_name' ''],
                                                                                        fl_name['last_name' '']]))
        app_list = "Whoops! Something went wrong. I couldn't find your permissions."
    attachment = msg_attachment.SlackAttachment(fallback=app_list, text=app_list,
                                                button_text="Open in People", button_url=pcoaddress)
    return attachment


if __name__ == '__main__':
    name = "john"
    email = "john@someemail.com"
    credentials = {"name": name, "email": email}
    app = "people"
    credentials = {"name": name, "email": email}
    print("Access to People: ", get(credentials, app))
    print("Apps you have access to: ", get_apps(credentials).slack())
