import datetime
import re
import time

from natural.date import day
import parsedatetime.parsedatetime as pdt


class NaturalTimeMixin(object):

    def strip_leading_zeros(self, date_str):
        date_str = date_str.replace(":0", "__&&")
        date_str = re.sub("0*(\d+)", "\g<1>", date_str)
        date_str = date_str.replace("__&&", ":0")
        return date_str

    def parse_natural_time(self, time_str):
        cal = pdt.Calendar()
        time_tuple = cal.parse(time_str)[0][:-2]

        return datetime.datetime(*time_tuple)

    def to_natural_day(self, dt):
        day_str = day(dt)
        return self.strip_leading_zeros(day_str)

    def to_natural_day_and_time(self, dt, with_timezone=False):
        if dt.minute == 0:
            if with_timezone:
                time_str = "%s %s" % (dt.strftime("%I%p").lower(), time.tzname[0])
            else:
                time_str = dt.strftime("%I%p").lower()
        else:
            if with_timezone:
                time_str = "%s %s" % (dt.strftime("%I:%M%p").lower(), time.tzname[0])
            else:
                time_str = dt.strftime("%I:%M%p").lower()

        full_str = "%s at %s" % (self.to_natural_day(dt), time_str)
        return self.strip_leading_zeros(full_str)
