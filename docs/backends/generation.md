# Generation Backends

## Overview
Generation backends are Will's equivalent of that momement when we pause, and run through all the possible things we could say.  Some of them are great ideas.  Some of them are terrible ideas.  But the process of _generation_ doesn't care - it's just about making as many ideas as possible.

Will's generation backends do the same thing - try to come up with things Will *could* say or do to respond to what he heard.

Will has the following generation backends built-in, and it's easy to add your own or contribute one to the project:

- Fuzzy Match (all) (`will.backends.generation.fuzzy_all_matches`)
- Fuzzy Match (best) (`will.backends.generation.fuzzy_best_match`)
- Strict Regex (`will.backends.generation.strict_regex`)


## Choosing your backends

Like our brain processes, we can have lots of different ways to generate ideas, working together.  You don't have to pick just one generation backend for Will.  Depending on your setup, it might be the more, the merrier.

Here's a bit more about the built-ins, and when they'd be a good fit:

### Fuzzy Match (all) (`will.backends.generation.fuzzy_all_matches`)

Great at..

### Fuzzy Match (best) (`will.backends.generation.fuzzy_best_match`)

Great at..

### Strict Regex (`will.backends.generation.strict_regex`)

Great at..


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

Now we've got a host of possible things Will can do and say.  It's time to look at how [Will decides what to do](/platform/execution).