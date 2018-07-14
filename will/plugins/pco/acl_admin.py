from will.plugin import WillPlugin
from will.decorators import respond_to, hear
from will.acl import get_acl_members, get_acl_groups
from will.plugins.pco import msg_attachment, authenticate
import will.abstractions


class AclAdmin(WillPlugin):
    @respond_to("(?:show | )?(!acl)(?P<acl_list>.*?(?=(?:\?)|$))", acl=["pastors", "staff"])
    def acl_lookup(self, message, acl_list):
        msg = ""
        attachment = []
        acl_groups = get_acl_groups()
        for acl in acl_groups:
            print(acl)
            msg += "*" + acl + ":*\n"
            print(msg)
            for x in get_acl_members(acl):
                print(x)
                msg += x + ", "
                print(msg)
            msg += "\n"
        attachment = msg_attachment.SlackAttachment(text=msg)
        print(attachment.slack())

        self.reply("Here are all the access control lists I have:", message=message, attachments=attachment.slack())

    @hear("(?:Can I |do I have )?(access |!app)(?P<app>.*?(?=(?:\?)|$))")
    def message_test(self, message, app):
        credentials = {"name": message.sender['source']['real_name'], "email": message.sender['source']['email']}
        print("This is what's in app: " + app)
        if app:
            print("checking credentials")
            if authenticate.get(credentials, app):
                self.reply("You have access to: " + app)
            else:
                self.reply("Sorry but you don't have access to that Planning Center App. "
                           "Please contact your administrator.")
        else:
            self.reply("Getting your permissions. . .", message=message)
            print("calling app_list")
            attachment = authenticate.get_apps(credentials)
            your_apps = attachment.slack()
            self.reply("Here are the apps you have access to: ", message=message, attachments=your_apps)


if __name__ == '__main__':
    acl = "pastors"
    get_acl_members(acl)
    list = get_acl_groups()
    print(str(list))