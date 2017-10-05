from will.utils import warn
from will.backends.storage.couchbase_backend import CouchbaseStorage

warn(
    "Deprecation - will.storage.couchbase_storage has been moved to will.backends.storage.couchbase_backend, " +
    "and will be removed in version 2.2.  Please update your paths accordingly!"
)
