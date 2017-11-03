
## Overview
We never communicate in the void - there's always a context, and things to read into a particular message, depending who said it, when, and how - and that's exactly what Will's analysis backends are for.  

They look at an incoming message and everything around it, and add context.

Will has the following analysis backends built-in, more are on the way (like sentiment analysis) and it's easy to make your own or contribute one to the project:

- History (`will.backends.analysis.history`)
- Nothing (`will.backends.analysis.nothing`)


## Choosing your backends


Here's a bit more about the built-ins, and when they'd be a good fit:

### History (`will.backends.analysis.history`)

Just adds the last 20 messages he heard into the context, and stores this one for the future.

### Nothing (`will.backends.analysis.nothing`)

Does absolutely nothing.  But it is a nice template for building your own!



Considerations, etc

## Setting your backends

`config.py`
required settings

## Contributing a new backend

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

Now we've got context, let's look at how [Will generates possibilities](/platform/generation).