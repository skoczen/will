"""Endpoints for PCO check_ins.

To add additional endpoints, simply add additional classes
subclassing the Check_insEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the check_ins endpoint
class Check_insEndpoint(BaseEndpoint): pass

# All objects on the check_ins endpoint
class AttendanceTypes(Check_insEndpoint): pass
class CheckIns(Check_insEndpoint): pass
class CheckInGroups(Check_insEndpoint): pass
class Events(Check_insEndpoint): pass
class EventLabels(Check_insEndpoint): pass
class EventPeriods(Check_insEndpoint): pass
class EventTimes(Check_insEndpoint): pass
class Headcounts(Check_insEndpoint): pass
class Labels(Check_insEndpoint): pass
class Locations(Check_insEndpoint): pass
class LocationEventPeriods(Check_insEndpoint): pass
class LocationEventTimes(Check_insEndpoint): pass
class LocationLabels(Check_insEndpoint): pass
class Options(Check_insEndpoint): pass
class Organizations(Check_insEndpoint): pass
class Passes(Check_insEndpoint): pass
class People(Check_insEndpoint): pass
class PersonEvents(Check_insEndpoint): pass
class Stations(Check_insEndpoint): pass
class Themes(Check_insEndpoint): pass
