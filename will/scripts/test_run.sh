#!/bin/bash

export WILL_USERNAME='12345_123456@chat.hipchat.com'
export WILL_PASSWORD='asj2498q89dsf89a8df'
export WILL_TOKEN='kjadfj89a34878adf78789a4fae3'
export WILL_V2_TOKEN='asdfjl234jklajfa3azfasj3afa3jlkjiau'
export WILL_ROOMS='Testing, Will Kahuna;GreenKahuna'  # Semicolon-separated, so you can have commas in names.
export WILL_NAME='William T. Kahuna'  # Must be the *exact, case-sensitive* full name from hipchat.
export WILL_HANDLE='will'  # Must be the exact handle from hipchat.
export WILL_REDIS_URL="redis://localhost:6379/7"

# Optional
export WILL_DEFAULT_ROOM='12345_room1@conf.hipchat.com'  # Default room: (otherwise defaults to the first of WILL_ROOMS)
export WILL_HANGOUT_URL='https://plus.google.com/hangouts/_/event/ceggfjm3q3jn8ktan7k861hal9o...'  # For google hangouts:
export WILL_DEFAULT_FROM_EMAIL="will@example.com"
export WILL_MAILGUN_API_KEY="key-12398912329381"
export WILL_MAILGUN_API_URL="example.com"

# For Production:
export WILL_HTTPSERVER_PORT="80"  # Port to listen to (defaults to $PORT, then 80.)
export WILL_URL="http://my-will.herokuapp.com" # If will isn't accessible at localhost (heroku, etc). No trailing slash.:

`find . -name "start_dev_will.py"` &
PID=$!
sleep 10
RUNNING=`ps a | grep start_dev_will | grep -v grep | wc -l`
if [ ${RUNNING} -gt 0 ]; then
    kill $PID
    ps a | grep start_dev_will | grep -v grep | awk '{print $1}' | xargs kill -9
    exit 0;
else
    exit 1;
fi
