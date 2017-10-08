import datetime
import pytz
import requests
import time

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings


def get_location(place):
    payload = {'address': place, 'sensor': False}
    r = requests.get('http://maps.googleapis.com/maps/api/geocode/json', params=payload)
    resp = r.json()
    location = resp["results"][0]["geometry"]["location"]
    return location


def get_timezone(lat, lng):
    payload = {'location': "%s,%s" % (lat, lng), 'timestamp': int(time.time()), 'sensor': False}
    r = requests.get('https://maps.googleapis.com/maps/api/timezone/json', params=payload)
    resp = r.json()
    tz = resp['timeZoneId']
    return tz


class TimePlugin(WillPlugin):

    @respond_to("what time is it in (?P<place>.*)")
    def what_time_is_it_in(self, message, place):
        """what time is it in ___: Say the time in almost any city on earth."""
        location = get_location(place)
        tz = get_timezone(location['lat'], location['lng'])
        ct = datetime.datetime.now(tz=pytz.timezone(tz))
        self.say("It's %s in %s." % (self.to_natural_day_and_time(ct), place), message=message)

    @respond_to("what time is it(\?)?$", multiline=False)
    def what_time_is_it(self, message):
        """what time is it: Say the time where I am."""
        now = datetime.datetime.now()
        self.say("It's %s." % self.to_natural_day_and_time(now, with_timezone=True), message=message)
