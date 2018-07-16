#!/usr/bin/env bash
#source bin/activate

export WILL_PCO_API_SECRET=""
export WILL_PCO_APPLICATION_KEY=""
export WILL_SLACK_API_TOKEN=""

#edit below, as specific to your installation of python in the virtual environment.
sudo -E /home/pi/pcobot/my_pcobot/bin/python ./start_dev_will.py
