import os

for k, v in os.environ.items():
    globals()[k] = v

if "WILL_ROOMS" in os.environ:
    WILL_ROOMS = WILL_ROOMS.split(";")

if not "WILL_DEFAULT_ROOM" in os.environ:
    WILL_DEFAULT_ROOM = WILL_ROOMS[0]

if not "WILL_HTTPSERVER_PORT" in os.environ:
    # For heroku
    if "PORT" in os.environ:
        WILL_HTTPSERVER_PORT = PORT
    else:
        WILL_HTTPSERVER_PORT = "80"

if not "WILL_URL" in os.environ:
    WILL_URL = "http://localhost:%s" % WILL_HTTPSERVER_PORT

