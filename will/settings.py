import os

for k, v in os.environ.items():
    globals()[k] = v

if "WILL_ROOMS" in globals():
    WILL_ROOMS = WILL_ROOMS.split(";")

if not "WILL_DEFAULT_ROOM" in globals():
    WILL_DEFAULT_ROOM = WILL_ROOMS[0]

if not "WILL_HTTPSERVER_PORT" in globals():
    WILL_HTTPSERVER_PORT = "80"

if not "WILL_URL" in globals():
    WILL_URL = "http://localhost:%s" % WILL_HTTPSERVER_PORT