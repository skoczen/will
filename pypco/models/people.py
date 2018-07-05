"""Models for PCO people.

To add additional models, simply add additional classes
subclassing the PeopleModel class.
"""

#pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base people model
class PeopleModel(BaseModel): pass

# People models
class Address(PeopleModel): ENDPOINT_NAME='addresses'
class App(PeopleModel): ENDPOINT_NAME='apps'
class Campus(PeopleModel): ENDPOINT_NAME='campuses'
class Carrier(PeopleModel): ENDPOINT_NAME='carriers'
class Condition(PeopleModel): ENDPOINT_NAME='lists'
class ConnectedPerson(PeopleModel): ENDPOINT_NAME='people'
class Email(PeopleModel): ENDPOINT_NAME='emails'
class FieldDatum(PeopleModel): ENDPOINT_NAME='field_data'
class FieldDefinition(PeopleModel): ENDPOINT_NAME='field_definitions'
class FieldOption(PeopleModel): ENDPOINT_NAME='field_options'
class Household(PeopleModel): ENDPOINT_NAME='households'
class HouseholdMembership(PeopleModel): ENDPOINT_NAME='people'
class InactiveReason(PeopleModel): ENDPOINT_NAME='inactive_reasons'
class List(PeopleModel): ENDPOINT_NAME='lists'
class ListCategories(PeopleModel): ENDPOINT_NAME='list_categories'
class ListShare(PeopleModel): ENDPOINT_NAME='lists'
class MailchimpSyncStatus(PeopleModel): ENDPOINT_NAME='lists'
class MaritalStatus(PeopleModel): ENDPOINT_NAME='marital_statuses'
class Message(PeopleModel): ENDPOINT_NAME='messages'
class MessageGroup(PeopleModel): ENDPOINT_NAME='message_groups'
class NamePrefix(PeopleModel): ENDPOINT_NAME='name_prefixes'
class NameSuffix(PeopleModel): ENDPOINT_NAME='name_suffixes'
class Notes(PeopleModel): ENDPOINT_NAME='notes'
class Organization(PeopleModel): ENDPOINT_NAME=''
class OrganizationalStatistics(PeopleModel): ENDPOINT_NAME='stats'
class PeopleImport(PeopleModel): ENDPOINT_NAME='people_imports'
class PeopleImportConflict(PeopleModel): ENDPOINT_NAME='people_imports'
class PeopleImportHistory(PeopleModel): ENDPOINT_NAME='people_imports'
class Person(PeopleModel): ENDPOINT_NAME='people'
class PersonApp(PeopleModel): ENDPOINT_NAME='person_apps'
class PersonMerger(PeopleModel): ENDPOINT_NAME='person_mergers'
class PhoneNumber(PeopleModel): ENDPOINT_NAME='phone_numbers'
class Report(PeopleModel): ENDPOINT_NAME='reports'
class Rule(PeopleModel): ENDPOINT_NAME='rules'
class SchoolOption(PeopleModel): ENDPOINT_NAME='school_options'
class SocialProfile(PeopleModel): ENDPOINT_NAME='social_profiles'
class Tab(PeopleModel): ENDPOINT_NAME='tabs'
class Workflow(PeopleModel): ENDPOINT_NAME='workflows' 
class WorkflowCard(PeopleModel): ENDPOINT_NAME='people'
class WorkflowCardActivity(PeopleModel): ENDPOINT_NAME='people'
class WorkflowCardNote(PeopleModel): ENDPOINT_NAME='people'
class WorkflowShare(PeopleModel): ENDPOINT_NAME='workflows'
class WorkflowStep(PeopleModel): ENDPOINT_NAME='workflows'
class WorkflowStepAssigneeSummary(PeopleModel): ENDPOINT_NAME='workflows'
