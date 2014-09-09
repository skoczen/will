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

def fuzzy_suffix(fuzziness):
    """Compose `regex` fuzziness control string, e.g. "{i<=1,d<=2} for one insertion and 2 deletions

    TODO: This scale may not be the most intuitive, consider somthing more natural
    >>> fuzzy_suffix(0)  
    ''
    >>> fuzzy_suffix(1)  # corresponds to allowed_typos = 0.3
    '{d<=1}'
    >>> fuzzy_suffix(2)  # allowed_typos = 0.6
    '{i<=1,d<=1}'
    >>> fuzzy_suffix(3)  # allowed_typos = 1
    '{e<=1}'
    >>> fuzzy_suffix(5)  # allowed_typos = 1.3
    '{i<=2,d<=2}'
    >>> fuzzy_suffix(6)  # allowed_typos = 1.6
    '{e<=2}'
    >>> fuzzy_suffix(7)  # allowed_typos = 2
    '{e<=3,d<=3}'
    >>> import regex
    >>> bool(regex.match('(hello)'+fuzzy_suffix(4), 'heo'))
    True
    """
    fuzzy_suffixes = []
    e = int((fuzziness + 1) / 3)
    if e:
        fuzzy_suffixes += ['e<=%d' % (int((fuzziness - 1) / 3) + 1)]
    if fuzziness % 3:
        fuzzy_suffixes +=  ['d<=%d' % (int(fuzziness / 3) + 1)]
        if not (fuzziness + 1) % 3:
            fuzzy_suffixes= ['i<=%d' % (int(fuzziness / 3) + 1)] + ['d<=%d' % (int(fuzziness / 3) + 1)]
    if fuzzy_suffixes:
        return '{%s}' % (','.join(fuzzy_suffixes))
    return ''

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
