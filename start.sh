#!/bin/sh
#source bin/activate

export WILL_PCO_API_SECRET=
export WILL_PCO_APPLICATION_KEY=
export WILL_SLACK_API_TOKEN=

sudo -E ./bin/python ./start_dev_will.py
