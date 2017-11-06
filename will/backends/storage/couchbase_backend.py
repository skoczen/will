from six.moves.urllib import parse

from couchbase import Couchbase, exceptions as cb_exc
from .base import BaseStorageBackend


class CouchbaseStorage(BaseStorageBackend):
    """
    A storage backend using Couchbase

    You must supply a COUCHBASE_URL setting that is passed through urlparse.
    All parameters supplied get passed through to Couchbase

    Examples:

    * couchbase:///bucket
    * couchbase://hostname/bucket
    * couchbase://host1,host2/bucket
    * couchbase://hostname/bucket?password=123abc&timeout=5
    """

    required_settings = [
        {
            "name": "COUCHBASE_URL",
            "obtain_at": """You must supply a COUCHBASE_URL setting that is passed through urlparse.
All parameters supplied get passed through to Couchbase

Examples:

* couchbase:///bucket
* couchbase://hostname/bucket
* couchbase://host1,host2/bucket
* couchbase://hostname/bucket?password=123abc&timeout=55""",
        },
    ]

    def __init__(self, settings):
        self.verify_settings(quiet=True)
        url = parse.urlparse(settings.COUCHBASE_URL)
        params = dict([
            param.split('=')
            for param in url.query.split('&')
        ])
        self.couchbase = Couchbase(host=url.hostname.split(','),
                                   bucket=url.path.strip('/'),
                                   port=url.port or 8091,
                                   **params)

    def do_save(self, key, value, expire=None):
        res = self.couchbase.set(key, value, ttl=expire)
        return res.success

    def clear(self, key):
        res = self.couchbase.delete(key)
        return res.success

    def clear_all_keys(self):
        """
        Couchbase doesn't support clearing all keys (flushing) without the
        Admin username and password.  It's not appropriate for Will to have
        this information so we don't support clear_all_keys for CB.
        """
        return "Sorry, you must flush the Couchbase bucket from the Admin UI"

    def do_load(self, key):
        try:
            res = self.couchbase.get(key)
            return res.value
        except cb_exc.NotFoundError:
            pass

    def size(self):
        """
        Couchbase doesn't support getting the size of the DB
        """
        return "Unknown (See Couchbase Admin UI)"


def bootstrap(settings):
    return CouchbaseStorage(settings)
