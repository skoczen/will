from will.utils import warn
from will.backends.storage.file_backend import FileStorage

warn(
    "Deprecation - will.storage.file_storage has been moved to will.backends.storage.file_backend, " +
    "and will be removed in version 2.2.  Please update your paths accordingly!"
)
