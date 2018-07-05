"""Models for PCO Resources.

To add additional models, simply add additional classes
subclassing the ResourcesModel class.
"""

#pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base Resources model
class ResourcesModel(BaseModel): pass

# Resources models
class Attachment(ResourcesModel): ENDPOINT_END='attachements'
class Conflict(ResourcesModel): ENDPOINT_END='conflicts'
class Event(ResourcesModel): ENDPOINT_END='events'
class EventInstance(ResourcesModel): ENDPOINT_END='event_instances'
class EventResourceRequest(ResourcesModel): ENDPOINT_END='event_resource_requests'
class EventTime(ResourcesModel): ENDPOINT_END='event_times'
class Organization(ResourcesModel): ENDPOINT_END='organizations'
class Peoples(ResourcesModel): ENDPOINT_END='people'
class Resource(ResourcesModel): ENDPOINT_END='resources'
class ResourceApprovalGroup(ResourcesModel): ENDPOINT_END='resource_approval_groups'
class ResourceBooking(ResourcesModel): ENDPOINT_END='resource_bookings'
class ResourceFolder(ResourcesModel): ENDPOINT_END='resources_folders'
class ResourceQuestion(ResourcesModel): ENDPOINT_END='resource_questions'
class RoomSetup(ResourcesModel): ENDPOINT_END='room_setups'
