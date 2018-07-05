"""Endpoints for PCO people.

To add additional endpoints, simply add additional classes
subclassing the PeopleEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the people endpoint
class PeopleEndpoint(BaseEndpoint): pass

# All objects on the people endpoint
class Addresses(PeopleEndpoint): pass
class Apps(PeopleEndpoint): pass
class Campuses(PeopleEndpoint): pass
class Carriers(PeopleEndpoint): pass
class Emails(PeopleEndpoint): pass
class FieldData(PeopleEndpoint): pass
class FieldDefinitions(PeopleEndpoint): pass
class Households(PeopleEndpoint): pass
class InactiveReasons(PeopleEndpoint): pass
class ListCategories(PeopleEndpoint): pass
class Lists(PeopleEndpoint): pass
class MaritalStatuses(PeopleEndpoint): pass
class MessageGroups(PeopleEndpoint): pass
class Messages(PeopleEndpoint): pass
class NamePrefixes(PeopleEndpoint): pass
class NameSuffixes(PeopleEndpoint): pass
class Notes(PeopleEndpoint): pass
class People(PeopleEndpoint): pass
class PeopleImports(PeopleEndpoint): pass
class PersonMergers(PeopleEndpoint): pass
class Reports(PeopleEndpoint): pass
class SchoolOptions(PeopleEndpoint): pass
class SocialProfiles(PeopleEndpoint): pass
class Stats(PeopleEndpoint): pass
class Tabs(PeopleEndpoint): pass
class Workflows(PeopleEndpoint): pass
