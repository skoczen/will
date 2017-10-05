from will.utils import warn
from will.backends.storage.redis_backend import RedisStorage

warn(
    "Deprecation - will.storage.redis_storage has been moved to will.backends.storage.redis_backend, " +
    "and will be removed in version 2.2.  Please update your paths accordingly!"
)
