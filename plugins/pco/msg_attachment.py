

class SlackAttachment:

    def __init__(self, fallback="", pco="people", text="",
                 button_color=None, action_type="button", button_text="Open in PCO", button_url=""):
        self.fallback = fallback
        self.text = text
        self.footer = "Planning Center Online API"
        if button_color is None:
            self.button_color = "#3B80C6"
        else:
            self.button_color = button_color
        if pco == "people":
            self.color = "#3B80C6"
            self.button_color = "#3B80C6"
            self.footer_icon = "https://d1pz3w4vu41eda.cloudfront.net/assets/people/" \
                               "favicon-128-9da4ee8f3ce3ec27b9ae86cceb4f3bb5c4e58c2becf38bee6850ff3923415e50.png"
        if pco == "services":
            self.color = "#0e8a16"
            self.button_color = "#0e8a16"
            self.footer_icon = "https://d1th6rei50eu1y.cloudfront.net/assets/services/" \
                               "favicon-128-54e6ba6447212021931bde30a181c31ec57056fd3d99d6e3a8b1bd0eddca7c1d.png"
        if pco == "check_ins":
            self.color = "#876096"
            self.button_color = "#876096"
            self.footer_icon = "https://d20n8yffv74pqs.cloudfront.net/assets/check-ins/" \
                               "favicon-128-4ba5f33023f9771353564e67c6e1e049b0e7eea2f0c881c58432a3adc93a44ab.png"
        if pco == "groups":
            self.color = "#FB7642"
            self.button_color = "#FB7642"
            self.footer_icon = "https://d1hyrr5xjek6kh.cloudfront.net/assets/groups/" \
                               "favicon-128-72f00b4c20882e96fc4490129f73de2860e1444ec3b2800dfd0120c36322b7ab.png"
        if pco == "giving":
            self.color = "#f4c551"
            self.button_color = "#f4c551"
            self.footer_icon = "https://d3pvtdriu5iusc.cloudfront.net/assets/giving/" \
                               "favicon-128-a70151fb5689841d8bd4f8fb64756c6421aae8d2076cbf656b46626175a38125.png"
        if pco == "registrations":
            self.color = "#007AB8"
            self.button_color = "#007AB8"
            self.footer_icon = "https://d141ugdjiohsni.cloudfront.net/assets/registrations/" \
                               "favicon-128-0c011b11e8e7ac883933b1004306d55485c08e8c3d95779a39b02caa92f47249.png"
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
    x = SlackAttachment(fallback="TEST", pco="check_ins")
    x.set_actions(text="test", url="google.com")
    print(x.slack())
