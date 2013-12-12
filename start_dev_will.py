#!/usr/bin/env python
from will.main import WillBot

if __name__ == '__main__':
    bot = WillBot(plugins_dirs=["plugins",], template_dirs=["templates",])
    bot.bootstrap()
