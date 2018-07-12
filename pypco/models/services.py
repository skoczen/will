"""Models for PCO people.

To add additional models, simply add additional classes
subclassing the ServicesModel class.
"""

# pylint: disable=C0321,R0903,C0111

from .base_model import BaseModel

# The base people model


class ServicesModel(BaseModel): pass

# Services models
class Arrangement(ServicesModel): ENDPOINT_NAME='arrangements'
class Attachment(ServicesModel): ENDPOINT_NAME='attachments'
class AttachmentActivity(ServicesModel): ENDPOINT_NAME='attachment_activities'
class AttachmentType(ServicesModel): ENDPOINT_NAME='attachment_types'
class AvailableSignup(ServicesModel): ENDPOINT_NAME='available_signups'
class BackgroundCheck(ServicesModel): ENDPOINT_NAME='background_checks'
class Blockout(ServicesModel): ENDPOINT_NAME='blockouts'
class BlockoutDate(ServicesModel): ENDPOINT_NAME='blockout_dates'
class BlockoutException(ServicesModel): ENDPOINT_NAME='blockout_exceptions'
class CheckIn(ServicesModel): ENDPOINT_NAME='checkins'
class Contributor(ServicesModel): ENDPOINT_NAME='contributors'
class EmailTemplate(ServicesModel): ENDPOINT_NAME='email_templates'
class EmailTemplateRenderedResponse(ServicesModel): ENDPOINT_NAME='email_template_rendered_responses'
class Folder(ServicesModel): ENDPOINT_NAME='folders'
class Item(ServicesModel): ENDPOINT_NAME='items'
class ItemNote(ServicesModel): ENDPOINT_NAME='item_notes'
class ItemNoteCategorie(ServicesModel): ENDPOINT_NAME='item_note_categories'
class ItemTime(ServicesModel): ENDPOINT_NAME='item_times'
class Key(ServicesModel): ENDPOINT_NAME='keys'
class Layout(ServicesModel): ENDPOINT_NAME='layouts'
class Media(ServicesModel): ENDPOINT_NAME='medias'
class MediaSchedule(ServicesModel): ENDPOINT_NAME='media_schedules'
class NeededPosition(ServicesModel): ENDPOINT_NAME='needed_positions'
class Organization(ServicesModel): ENDPOINT_NAME='organizations'
class Peoples(ServicesModel): ENDPOINT_NAME='people'
class PersonTeamPositionAssignment(ServicesModel): ENDPOINT_NAME='person_tem_position_assignments'
class Plan(ServicesModel): ENDPOINT_NAME='plans'
class PlanNote(ServicesModel): ENDPOINT_NAME='plan_notes'
class PlanNoteCategorie(ServicesModel): ENDPOINT_NAME='plan_note_categories'
class PlanPeoples(ServicesModel): ENDPOINT_NAME='plan_people'
class PlanPersonTime(ServicesModel): ENDPOINT_NAME='plan_person_times'
class PlanTemplate(ServicesModel): ENDPOINT_NAME='plan_templates'
class PlanTime(ServicesModel): ENDPOINT_NAME='plan_times'
class Schedule(ServicesModel): ENDPOINT_NAME='schedules'
class ScheduledPeoples(ServicesModel): ENDPOINT_NAME='scheduled_people'
class Serie(ServicesModel): ENDPOINT_NAME='series'
class ServiceType(ServicesModel): ENDPOINT_NAME='service_types'
class SignupSheet(ServicesModel): ENDPOINT_NAME='signup_sheets'
class SignupSheetMetadatum(ServicesModel): ENDPOINT_NAME='signup_sheet_metadata'
class SkippedAttachment(ServicesModel): ENDPOINT_NAME='skipped_attachments'
class Song(ServicesModel): ENDPOINT_NAME='songs'
class SongSchedule(ServicesModel): ENDPOINT_NAME='song_schedules'
class SplitTeamRehearsalAssignment(ServicesModel): ENDPOINT_NAME='split_team_rehersal_assignments'
class Tag(ServicesModel): ENDPOINT_NAME='tags'
class TagGroup(ServicesModel): ENDPOINT_NAME='tag_groups'
class Team(ServicesModel): ENDPOINT_NAME='teams'
class TeamLeader(ServicesModel): ENDPOINT_NAME='team_leaders'
class TeamPosition(ServicesModel): ENDPOINT_NAME='team_positions'
class TextSetting(ServicesModel): ENDPOINT_NAME='text_settings'
class TimePreferenceOption(ServicesModel): ENDPOINT_NAME='time_preference_options'
class Zoom(ServicesModel): ENDPOINT_NAME='zooms'
