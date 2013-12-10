#!/usr/bin/env python
import logging
from will.main import WillBot

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
    bot = WillBot()
    bot.bootstrap()

    print "\nExiting."
