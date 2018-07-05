"""Models for PCO check_ins.

To add additional models, simply add additional classes
subclassing the Check_insModel class.
"""

#pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base check_ins model
class Check_insModel(BaseModel): pass

# Check_ins models
class AttendanceType(Check_insModel): ENDPOINT_NAME='attendance_types'
class CheckIn(Check_insModel): ENDPOINT_NAME='checkins'
class CheckInGroup(Check_insModel): ENDPOINT_NAME='checkin_groups'
class Event(Check_insModel): ENDPOINT_NAME='events'
class EventLabel(Check_insModel): ENDPOINT_NAME='event_labels'
class EventPeriod(Check_insModel): ENDPOINT_NAME='event_periods'
class EventTime(Check_insModel): ENDPOINT_NAME='event_times'
class Headcount(Check_insModel): ENDPOINT_NAME='headcounts'
class Label(Check_insModel): ENDPOINT_NAME='labels'
class Location(Check_insModel): ENDPOINT_NAME='locations'
class LocationEventPeriod(Check_insModel): ENDPOINT_NAME='location_event_periods'
class LocationEventTime(Check_insModel): ENDPOINT_NAME='location_event_periods'
class LocationLabel(Check_insModel): ENDPOINT_NAME='location_labels'
class Option(Check_insModel): ENDPOINT_NAME='options'
class Organization(Check_insModel): ENDPOINT_NAME='organizations'
class Pass(Check_insModel): ENDPOINT_NAME='passes'
class Peoples(Check_insModel): ENDPOINT_NAME='people'
class PersonEvent(Check_insModel): ENDPOINT_NAME='person_events'
class Station(Check_insModel): ENDPOINT_NAME='stations'
class Theme(Check_insModel): ENDPOINT_NAME='themes'
