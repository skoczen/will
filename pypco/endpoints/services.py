"""Endpoints for PCO services.

To add additional endpoints, simply add additional classes
subclassing the ServicesEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the services endpoint
class ServicesEndpoint(BaseEndpoint): pass

# All objects on the services endpoint
class Arrangements(ServicesEndpoint): pass
class Attachments(ServicesEndpoint): pass
class AttachmentActivities(ServicesEndpoint): pass
class AttachmentTypes(ServicesEndpoint): pass
class AvailableSignups(ServicesEndpoint): pass
class BackgroundChecks(ServicesEndpoint): pass
class Blockouts(ServicesEndpoint): pass
class BlockoutDates(ServicesEndpoint): pass
class BlockoutExceptions(ServicesEndpoint): pass
class CheckIns(ServicesEndpoint): pass
class Contributors(ServicesEndpoint): pass
class EmailTemplates(ServicesEndpoint): pass
class EmailTemplateRenderedResponses(ServicesEndpoint): pass
class Folders(ServicesEndpoint): pass
class Items(ServicesEndpoint): pass
class ItemNotes(ServicesEndpoint): pass
class ItemNoteCategories(ServicesEndpoint): pass
class ItemTimes(ServicesEndpoint): pass
class Keys(ServicesEndpoint): pass
class Layouts(ServicesEndpoint): pass
class Medias(ServicesEndpoint): pass
class MediaSchedules(ServicesEndpoint): pass
class NeededPositions(ServicesEndpoint): pass
class Organizations(ServicesEndpoint): pass
class People(ServicesEndpoint): pass
class PersonTeamPositionAssignments(ServicesEndpoint): pass
class Plans(ServicesEndpoint): pass
class PlanNotes(ServicesEndpoint): pass
class PlanNoteCategories(ServicesEndpoint): pass
class PlanPeople(ServicesEndpoint): pass
class PlanPersonTimes(ServicesEndpoint): pass
class PlanTemplates(ServicesEndpoint): pass
class PlanTimes(ServicesEndpoint): pass
class Schedules(ServicesEndpoint): pass
class ScheduledPeople(ServicesEndpoint): pass
class Series(ServicesEndpoint): pass
class ServiceTypes(ServicesEndpoint): pass
class SignupSheets(ServicesEndpoint): pass
class SignupSheetMetadata(ServicesEndpoint): pass
class SkippedAttachments(ServicesEndpoint): pass
class Songs(ServicesEndpoint): pass
class SongSchedules(ServicesEndpoint): pass
class SplitTeamRehearsalAssignments(ServicesEndpoint): pass
class Tags(ServicesEndpoint): pass
class TagGroups(ServicesEndpoint): pass
class Teams(ServicesEndpoint): pass
class TeamLeaders(ServicesEndpoint): pass
class TeamPositions(ServicesEndpoint): pass
class TextSettings(ServicesEndpoint): pass
class TimePreferenceOptions(ServicesEndpoint): pass
class Zooms(ServicesEndpoint): pass
