from will.plugin import WillPlugin
from will.decorators import respond_to
from will.acl import get_acl_members, get_acl_groups
from will.plugins.pco import msg_attachment


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


if __name__ == '__main__':
    acl = "pastors"
    get_acl_members(acl)
    list = get_acl_groups()
    print(str(list))
