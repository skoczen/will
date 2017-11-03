# Publish-Subscribe (Pubsub) Backends

## Overview
Pubsub backends handle all the internal messaging between Will's core components.  They're designed to be lightweight, reliable, and ephemeral - a lot like our brain's working memory.

Will supports the following options for pubsub backend:

- Redis (`will.backends.pubsub.redis`)

## Choosing a backend

## Setting your backend

`config.py`
required settings

## Contributing a new backend

Writing a new pubsub backend is fairly straightforward - simply subclass `BasePubSub`, and implement:

1) the four required methods, and
2) a bootstrap method.

```python
from will.backends.pubsub.base import BasePubSub


class MyCustomPubsubBackend(BasePubSub):
    """A custom pubsub backend using the latest, greatest framework.

    You'll need to provide a GREAT_API_KEY to use it.

    """"
    required_settings = [
        {
            "name": "GREAT_API_KEY",
            "obtain_at": """1. Go to greatamazingframework.com/api
2. Click "Generate API Key"
3. Copy that key, and set it in your Will.
""",
        },
    ]

    def __init__(self, settings):
        # Do whatever I need to do to kick off the backend.

    def do_subscribe(self, topic):
        """
        Registers with the backend to only get messages matching a specific topic.
        Where possible, wildcards are allowed
        """
        raise NotImplementedError

    def do_unsubscribe(self, topic):
        """Unregisters with the backend for a given topic."""
        raise NotImplementedError

    def publish_to_backend(self, topic, str):
        """Publishes a string to the backend with a given topic."""
        raise NotImplementedError

    def get_from_backend(self):
        """
        Gets the latest pending message from the backend (FIFO).
        Returns None if no messages are pending, and is expected *not* to be blocking.
        """
        raise NotImplementedError

def bootstrap(settings)
    MyCustomPubsubBackend(settings)

```

From there, just test it out, and submit a [pull request!](https://github.com/skoczen/will/pulls)

That's it for Will's pubsub backends.  He can also remember things long-term.  For that, read up on his [long-term memory (storage)](/platform/storage).