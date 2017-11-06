# IO Backends

## Overview
IO backends are how Will talks and listens to the outside world.  They're designed to abstract away the technical intracies of interfacing with a given platform, and let users just _use_ them.

Will supports the following io backends:

- Slack (`will.backends.storage.slack`)
- Hipchat (`will.backends.storage.hipchat`)
- Rocket.Chat (`will.backends.storage.rocketchat`)
- Shell (`will.backends.storage.shell`)


## Choosing your backends

This isn't a zero-sum game with will.  You can use as many backends as you'd like, all at once.


## Setting your backends

To set your io backends, just update the following in `config.py`

```python
# Platforms and mediums messages can come in and go out on.
IO_BACKENDS = [
    "will.backends.io_adapters.slack",
    "will.backends.io_adapters.hipchat",
    "will.backends.io_adapters.rocketchat",
    "will.backends.io_adapters.shell",
]
```

## Implementing a new backend

Writing a new storage backend is fairly straightforward - simply subclass `BaseStorageBackend`, and implement:

1. the five required methods, then
2. specify any required settings with `required_settings`.


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

Now that you've got hearing and talking sorted, let's look at how [Will adds context](/backends/analysis).