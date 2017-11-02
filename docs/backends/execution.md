# Execution Backends

## Overview
After we've thought of all the possibilities, we then have to decide what we want to do or say.  That's where Will's execution backends come in.

They take the context created by `analysis`, and the options created by `generation`, and make a decision on what to do.

Will has the following execution backends built-in, and it's easy to make your own or contribute one to the project:

- All (`will.backends.execution.all`)
- Best Score (`will.backends.execution.best_score`)


## Choosing your backends


Here's a bit more about the built-ins, and when they'd be a good fit:

### All (`will.backends.execution.all`)

![All the things](../img/all_the_things.jpg)

This is Will's crazy, do-everything mode.  He'll take every idea he got in the generation cycle and do *all* of them.  Why?  Because he's crazy like that.

Or, more likely, because you've built a custom generation backend that limits him down to a set of options you always want done.


### Best Score (`will.backends.execution.best_score`)

This is the right fit for most people, and it's the most similar to how our brains work.  Will looks at the options he has, and picks the single one he thinks is the best.



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