"""Models for PCO Giving.

To add additional models, simply add additional classes
subclassing the GivingModel class.
"""

#pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base Giving model
class GivingModel(BaseModel): pass

# Giving models
class Batch(GivingModel): ENDPOINT_END='batches'
class BatchGroup(GivingModel): ENDPOINT_END='batch_groups'
class Designation(GivingModel): ENDPOINT_END='designations'
class DesignationRefund(GivingModel): ENDPOINT_END='designation_refunds'
class Donation(GivingModel): ENDPOINT_END='donations'
class Fund(GivingModel): ENDPOINT_END='funds'
class Label(GivingModel): ENDPOINT_END='labels'
class Organization(GivingModel): ENDPOINT_END='organizations'
class PaymentMethod(GivingModel): ENDPOINT_END='payment_methods'
class PaymentSource(GivingModel): ENDPOINT_END='payment_sources'
class Peoples(GivingModel): ENDPOINT_END='people'
class RecurringDonation(GivingModel): ENDPOINT_END='recurring_donations'
class RecurringDonationDesignation(GivingModel): ENDPOINT_END='recurring_donation_designations'
class Refunds(GivingModel): ENDPOINT_END='refund'
