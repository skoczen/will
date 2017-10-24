#!/usr/bin/env python
from will.main import WillBot
import os
import shutil


def start_will():
    try:
        shutil.rmtree('will_profiles')
    except OSError:
        pass
    os.makedirs("will_profiles")

    bot = WillBot()
    bot.bootstrap()


if __name__ == '__main__':
    start_will()
