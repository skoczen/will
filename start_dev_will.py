#!/usr/bin/env python
import argparse
import os
import shutil
import sys
from will.main import WillBot

parser = argparse.ArgumentParser()
parser.add_argument(
    '--profile',
    action='store_true',
    help='Run with yappi profiling.'
)
args = parser.parse_args()


def start_will():
    if args.profile:
        try:
            import yappi
        except:
            print "Unable to run Will in profiling mode without yappi.  Please `pip install yappi`."
            sys.exit(1)
        try:
            shutil.rmtree('will_profiles')
        except OSError:
            pass
        os.makedirs("will_profiles")

    bot = WillBot()
    bot.bootstrap()


if __name__ == '__main__':
    start_will()
