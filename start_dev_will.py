#!/usr/bin/env python
from will.main import WillBot
import argparse

def csv(value):
    return map(lambda s: s.strip(), value.split(","))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='start a development configuration of will the chatbot',
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--plugins', type=csv, nargs='?', help="plugin directory paths", default=["plugins",])
    parser.add_argument('-t', '--templates', type=csv, nargs='?', help="template directory paths", default=["templates",])
    args = parser.parse_args()
    bot = WillBot(plugins_dirs=args.plugins, template_dirs=args.templates)
    bot.bootstrap()
