# Storage Backends

## Overview
Storage backends handle all of Will's long-term memory  They're designed to be durable, reliable, and robust - a lot like our brain's long-term memory, but without the forgetfulness.

Will supports the following options for storage backend:

- Redis (`will.backends.storage.redis`)
- Couchbase (`will.backends.storage.couchbase`)
- File (`will.backends.storage.file`)

## Choosing a backend

In general, we recommend using Redis, especially since for v2.0, it's also required for pubsub to get Will working.  However, in the future, we'll have more pubsub options, and this will be a more option choice.

If you're running in an environment with no access to external resources or ability to install packages, the `File` backend will get you sorted.  If you're already running Couchbase for various reasons, it might make the most sense to use it.

But for the moment, for most configurations, we recommend Redis.  It's stable, fast, well-supported, and just works.


## Setting your backends

To set your storage backend, just update the following in `config.py`

```python
STORAGE_BACKEND = "redis"  # "redis", "couchbase", or "file".
```

## Contributing a new backend

Writing a new storage backend is fairly straightforward - simply subclass `BaseStorageBackend`, and implement:

1) the five required methods, then
2) specify any required settings with `required_settings`.


```python
from will.backends.storage.base import BaseStorageBackend


class MyCustomStorageBackend(BaseStorageBackend):
    """A custom storage backend using the latest, greatest technology.

    You'll need to provide a GREAT_API_KEY to use it.

    """"

    required_settings = [
        {
            "name": "GREAT_API_KEY",
            "obtain_at": """1. Go to greatamazingtechnology.com/api
2. Click "Generate API Key"
3. Copy that key, and set it in your Will.
""",
        },
    ]


    # All storage backends must supply the following methods:    
    def __init__(self, *args, **kwargs):
        # Connects to the storage provider.

    def do_save(self, key, value, expire=None):
        raise NotImplemented

    def do_load(self, key):
        raise NotImplemented

    def clear(self, key):
        raise NotImplemented

    def clear_all_keys(self):
        raise NotImplemented

```

From there, just test it out, and when you're ready, submit a [pull request!](https://github.com/skoczen/will/pulls)

That's all you need to know to tweak and improve Will's memory.  There's just one topic left in his brain - keeping things private with [encryption](/platform/encryption).