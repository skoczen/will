
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

*Required settings*: None


### Nothing (`will.backends.analysis.nothing`)

Does absolutely nothing.  But it is a nice template for building your own!

*Required settings*: None


For the moment, there's no reason not to just include both built-in backends.  But as Will grows and additional options are added, these documents will be updated to explain the tradeoffs in enabling or disabling certain backends.

## Setting your backends

To set your analysis backends, just update the following in `config.py`

```python
# Backends to analyze messages and generate useful metadata
ANALYZE_BACKENDS = [
    "will.backends.analysis.nothing",
    "will.backends.analysis.history",
]
```


## Contributing a new backend

Writing a new analysis backend is fairly straightforward - simply subclass `BaseStorageBackend`, and implement the do_analysis method:


```python
from will.backends.analysis.base import AnalysisBackend

class NewBackend(AnalysisBackend):

    def do_analyze(self, message):
        # Do smart stuff
        return {
            "smart": "stuff",
            "cool": "things",
        }

```

From there, just test it out, and when you're ready, submit a [pull request!](https://github.com/skoczen/will/pulls)

Now we've got context, let's look at how [Will generates possibilities](/platform/generation).