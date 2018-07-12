"""Models for PCO Webhooks.

To add additional models, simply add additional classes
subclassing the WebhooksModel class.
"""

# pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base Webhooks model


class WebhooksModel(BaseModel): pass

# Webhooks models


class AvailableEvent(WebhooksModel): ENDPOINT_END='available_events'


class Deliverie(WebhooksModel): ENDPOINT_END='deliveries'


class Event(WebhooksModel): ENDPOINT_END='events'


class Organization(WebhooksModel): ENDPOINT_END='organizations'


class Subscription(WebhooksModel): ENDPOINT_END='subscriptions'
