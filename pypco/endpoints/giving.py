"""Endpoints for PCO Giving.

To add additional endpoints, simply add additional classes
subclassing the GivingEndpoint class.
"""

#pylint: disable=C0304,R0903,C0111,C0321

from .base_endpoint import BaseEndpoint

# The the Giving endpoint
class GivingEndpoint(BaseEndpoint): pass

# All objects on the Giving endpoint
class Batches(GivingEndpoint): pass
class BatchGroups(GivingEndpoint): pass
class Designations(GivingEndpoint): pass
class DesignationRefunds(GivingEndpoint): pass
class Donations(GivingEndpoint): pass
class Funds(GivingEndpoint): pass
class Labels(GivingEndpoint): pass
class Organizations(GivingEndpoint): pass
class PaymentMethods(GivingEndpoint): pass
class PaymentSources(GivingEndpoint): pass
class People(GivingEndpoint): pass
class RecurringDonations(GivingEndpoint): pass
class RecurringDonationDesignations(GivingEndpoint): pass
class Refund(GivingEndpoint): pass

