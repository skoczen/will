"""Endpoints for PCO Resources.

To add additional endpoints, simply add additional classes
subclassing the ResourcesEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the Resources endpoint
class ResourcesEndpoint(BaseEndpoint): pass

# All objects on the Resources endpoint
class Attachments(ResourcesEndpoint): pass
class Conflicts(ResourcesEndpoint): pass
class Events(ResourcesEndpoint): pass
class EventInstances(ResourcesEndpoint): pass
class EventResourceRequests(ResourcesEndpoint): pass
class EventTimes(ResourcesEndpoint): pass
class Organizations(ResourcesEndpoint): pass
class People(ResourcesEndpoint): pass
class Resources(ResourcesEndpoint): pass
class ResourceApprovalGroups(ResourcesEndpoint): pass
class ResourceBookings(ResourcesEndpoint): pass
class ResourceFolders(ResourcesEndpoint): pass
class ResourceQuestions(ResourcesEndpoint): pass
class RoomSetups(ResourcesEndpoint): pass

