import os

for k, v in os.environ.items():
    globals()[k] = v

if "WILL_ROOMS" in globals():
    WILL_ROOMS = WILL_ROOMS.split(";")
    print "WILL_ROOMS"
    print WILL_ROOMS