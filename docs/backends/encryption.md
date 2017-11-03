# Encryption Backends

## Overview
Encryption backends are what lets Will keep his thoughts private - safe from prying eyes, and would-be spies.

All of Will's short and long-term memory (`pubsub` and `storage`) are encrypted by default.

Will supports the following options for storage backend, and improvements and more backends are welcome:

- AES (`will.backends.storage.aes`)

## Choosing a backend

Considerations, etc

Will's AES backend uses AES in CBC mode to encrypt.

## Setting your backend

`config.py`
required settings

## Creating a new backend

## Implementing a new backend

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

That's Will's brain, end-to-end.  If you haven't already, dig into how to get him [deployed](/deploy.md)!