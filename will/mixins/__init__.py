from errors import ErrorMixin
from email import EmailMixin
from naturaltime import NaturalTimeMixin
from room import RoomMixin
from plugins_library import PluginModulesLibraryMixin
from schedule import ScheduleMixin
from settings import SettingsMixin
from sleep import SleepMixin
from storage import StorageMixin
from pubsub import PubSubMixin

# RosterMixin has been moved to from will.backends.io_adapters.hipchat import HipChatRosterMixin
# This is just for logging a warning for people who have used it internally
from roster import RosterMixin
