# -*- coding: utf-8 -*-
from clint.textui import puts, indent
from clint.textui import colored
from HTMLParser import HTMLParser


class Bunch(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


# Via http://stackoverflow.com/a/925630
class HTMLStripper(HTMLParser):
    def __init__(self):
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
    from . import settings
    return settings.ADMINS == '*' or nick.lower() in settings.ADMINS


def show_valid(valid_str):
    puts(colored.green(u"✓ %s" % valid_str))


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
