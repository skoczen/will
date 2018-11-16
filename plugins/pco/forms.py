import pypco
import os
from plugins.pco.msg_attachment import SlackAttachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get_forms():
    attachment_list = []
    for x in pco.people.forms.list():
        text = "\n".join([str(x.name),
                          str("Description: %s" % x.description)])
        attachment = SlackAttachment(x.name, text=text,
                                     button_text="Public Form",
                                     button_url=x.public_url)
        attachment.add_button(text="Submissions %s" % x.submission_count, url="https://people.planningcenteronline.com"
                                                                              "/forms/" + x.id +
                                                                              "/submissions")
        attachment_list.append(attachment)
    return attachment_list


if __name__ == '__main__':
    msg = get_forms()
    for m in msg:
        print(m.slack())
