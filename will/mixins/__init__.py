from will.mixins.errors import ErrorMixin
from will.mixins.email import EmailMixin
from will.mixins.naturaltime import NaturalTimeMixin
from will.mixins.room import RoomMixin
from will.mixins.plugins_library import PluginModulesLibraryMixin
from will.mixins.schedule import ScheduleMixin
from will.mixins.settings import SettingsMixin
from will.mixins.sleep import SleepMixin
from will.mixins.storage import StorageMixin
from will.mixins.pubsub import PubSubMixin

# RosterMixin has been moved to from will.backends.io_adapters.hipchat import HipChatRosterMixin
# This is just for logging a warning for people who have used it internally
from will.mixins.roster import RosterMixin
