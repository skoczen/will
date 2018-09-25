

class SlackAttachment:

    def __init__(self, fallback="", style="default", text="",
                 button_color=None, action_type="button", button_text="Open Link", button_url=""):
        """Set your own custom styles here."""
        self.fallback = fallback
        self.text = text
        self.footer = "Default Footer Text"
        if button_color is None:
            self.button_color = "#3B80C6"
        else:
            self.button_color = button_color
        if style == "default":
            self.color = "#555555"
            self.button_color = "#555555"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "blue":
            self.color = "#36a64f"
            self.button_color = "#36a64f"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "green":
            self.color = "#0e8a16"
            self.button_color = "#0e8a16"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "purple":
            self.color = "#876096"
            self.button_color = "#876096"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "orange":
            self.color = "#FB7642"
            self.button_color = "#FB7642"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "yellow":
            self.color = "#f4c551"
            self.button_color = "#f4c551"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        if style == "teal":
            self.color = "#007AB8"
            self.button_color = "#007AB8"
            self.footer_icon = "http://heywill.io/img/favicon.png"
        self.action_type = action_type
        self.button_text = button_text
        self.button_url = button_url
        self.actions = [
            {
                "color": self.button_color,
                "type": self.action_type,
                "text": self.button_text,
                "url": self.button_url
            }
        ]

    def dump(self):
        print("dump")
        print(self.fallback)
        print(self.text)
        print(self.button_url)
        pass

    def txt(self):
        text = " ".join([self.text])
        return text

    def set_actions(self, text, url):
        self.button_text = text
        self.button_url = url

    def add_button(self, text, url=None, button_color=None, button_action_type="button",):
        if url is None:
            url = "No URL"
        if button_color is None:
            button_color = self.button_color

        self.actions += [
                {
                    "color": button_color,
                    "type": button_action_type,
                    "text": text,
                    "url": url
                }
            ]

    def slack(self):
        attachment = [
                    {
                        "fallback": self.fallback,
                        "color": self.color,
                        "text": self.text,
                        "actions": self.actions,
                        "footer": self.footer,
                        "footer_icon": self.footer_icon,
                        }
        ]
        return attachment


if __name__ == '__main__':
    """Here's a demo of how to use the slack attachment. First create your attachment object.
    You can fill all the data at initilization."""
    demo_attachment = SlackAttachment(
        fallback="This is incase webcontent doesn't load. Here's the sample content!",
        text="Here's the sample content!",
        style="yellow",
        button_text="Click Me!",
        button_url="http://heywill.io")
    """We can add as many buttons as we like after initialization"""
    demo_attachment.set_actions(text="Go to google!", url="google.com")
    """You can dump a slack ready json attachment using .slack()"""
    print("Here's a slack formated json attachment:\n %s" % demo_attachment.slack() + '\n\n')
    """You can dump plain txt using .txt """
    print("Here's a txt version of the attachment:\n %s" % demo_attachment.txt() + '\n\n')
    """Package multiple attachments and append them to a list."""
    x = ['Ron', 'Bill', 'Gina', 'Rachael']
    attachments = []
    for i in x:
        attachments.append(SlackAttachment(fallback='The name is %s' % i,
                                           style='yellow',
                                           text='The name is %s' % i,
                                           button_text='Open in database',
                                           button_url='https://my.database.url/people/v2/' + i))
    """Unpack somewhere else"""
    demo2_attachment = ""
    for a in attachments:
        demo2_attachment += str(a.slack())
    print("Here's multiple attachments ready to send:\n %s" % demo2_attachment)
