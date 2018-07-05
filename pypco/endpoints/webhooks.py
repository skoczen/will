"""Endpoints for PCO Webhooks.

To add additional endpoints, simply add additional classes
subclassing the WebhooksEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the Webhooks endpoint
class WebhooksEndpoint(BaseEndpoint): pass

# All objects on the Webhooks endpoint
class AvailableEvents(WebhooksEndpoint): pass
class Deliveries(WebhooksEndpoint): pass
class Events(WebhooksEndpoint): pass
class Organizations(WebhooksEndpoint): pass
class Subscriptions(WebhooksEndpoint): pass
