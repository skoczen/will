import datetime
import logging
import pytz
import requests
import time

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings

logger = logging.getLogger(__name__)


class GoogleLocation(object):
    def __init__(self, google_results, *args, **kwargs):
        self.name = google_results["results"][0]["formatted_address"]
        self.lat = google_results["results"][0]["geometry"]["location"]["lat"]
        self.long = google_results["results"][0]["geometry"]["location"]["lng"]


def get_location(place):
    try:
        payload = {'address': place, 'sensor': False}
        r = requests.get('http://maps.googleapis.com/maps/api/geocode/json', params=payload)
        resp = r.json()
        if resp["status"] != "OK":
            return None
        else:
            location = GoogleLocation(resp)

            return location
    except Exception as e:
        logger.error("Failed to fetch geocode for %(place)s. Error %(error)s" % {'place': place, 'error': e})
        return None


def get_timezone(lat, lng):
    try:
        payload = {'location': "%(latitude)s,%(longitude)s" % {'latitude': lat,
                                                               'longitude': lng},
                   'timestamp': int(time.time()),
                   'sensor': False}
        r = requests.get('https://maps.googleapis.com/maps/api/timezone/json', params=payload)
        resp = r.json()
        if resp["status"] == "OK":
            tz = resp['timeZoneId']
            return tz
        else:
            return None
    except Exception as e:
        logger.error("Failed to fetch timezone for %(lat)s,%(lng)s. Error %(error)s" % {'lat': lat,
                                                                                        'lng': lng,
                                                                                        'error': e})
        return None


class TimePlugin(WillPlugin):

    @respond_to("what time is it in (?P<place>.*)?\?+")
    def what_time_is_it_in(self, message, place):
        """what time is it in ___: Say the time in almost any city on earth."""
        location = get_location(place)
        if location is not None:
            tz = get_timezone(location.lat, location.long)
            if tz is not None:
                ct = datetime.datetime.now(tz=pytz.timezone(tz))
                self.say("It's %(time)s in %(place)s." % {'time': self.to_natural_day_and_time(ct),
                                                          'place': location.name}, message=message)
            else:
                self.say("I couldn't find timezone for %(place)s." % {'place': location.name}, message=message)
        else:
            self.say("I couldn't find anywhere named %(place)s." % {'place': location.name}, message=message)

    @respond_to("what time is it(\?)?$", multiline=False)
    def what_time_is_it(self, message):
        """what time is it: Say the time where I am."""
        now = datetime.datetime.now()
        self.say("It's %s." % self.to_natural_day_and_time(now, with_timezone=True), message=message)
