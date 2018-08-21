# -*- coding: utf-8 -*-
from clint.textui import puts, colored
from six.moves import html_parser


UNSURE_REPLIES = [
    "Hmm.  I'm not sure what to say.",
    "I didn't understand that.",
    "I heard you, but I'm not sure what to do.",
    "I'm not sure what that means.",
]

DO_NOT_PICKLE = [
    "api_requester",
    "dnapi_requester",
    "websocket",
    "parse_channel_data",
    "server",
    "send_message",
    "_updatedAt",
]


class Bunch(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


def clean_for_pickling(d):
    cleaned_obj = Bunch()
    if hasattr(d, "items"):
        for k, v in d.items():
            if k not in DO_NOT_PICKLE and "__" not in k:
                cleaned_obj[k] = v
    else:
        for k in dir(d):
            if k not in DO_NOT_PICKLE and "__" not in k:
                cleaned_obj[k] = getattr(d, k)

    return cleaned_obj


# Via http://stackoverflow.com/a/925630
class HTMLStripper(html_parser.HTMLParser):
    def __init__(self):
        self.convert_charrefs = True
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def html_to_text(html):
    # Do some light cleanup.
    html = html.replace("\n", "").replace("<br>", "\n").replace("<br/>", "\n").replace('<li>', "\n - ")
    # Strip the tags
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()


def is_admin(nick):
    from will import settings
    return settings.ADMINS == '*' or nick.lower() in settings.ADMINS


def show_valid(valid_str):
    puts(colored.green(u"✓ %s" % valid_str))


def show_invalid(valid_str):
    puts(colored.red(u"✗ %s" % valid_str))


def warn(warn_string):
    puts(colored.yellow("! Warning: %s" % warn_string))


def error(err_string):
    puts(colored.red("ERROR: %s" % err_string))


def note(warn_string):
    puts(colored.cyan("- Note: %s" % warn_string))


def print_head():
        puts("""
      ___/-\___
  ___|_________|___
     |         |
     |--O---O--|
     |         |
     |         |
     |  \___/  |
     |_________|

      Will: Hi!
""")


def sizeof_fmt(num, suffix='B'):
    # http://stackoverflow.com/a/1094933
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
