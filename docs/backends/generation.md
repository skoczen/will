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

This uses the fantastic [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) library to match strings with some fuzziness, as specified by `FUZZY_MINIMUM_MATCH_CONFIDENCE` (defaults to 90% confidence) and `FUZZY_REGEX_ALLOWABLE_ERRORS` (defaults to 3).

Great if you'd like your Will to be a little flexible, sometimes get things wrong, but to handle typos.

*Required settings*: `FUZZY_MINIMUM_MATCH_CONFIDENCE` and `FUZZY_REGEX_ALLOWABLE_ERRORS`

### Fuzzy Match (best) (`will.backends.generation.fuzzy_best_match`)

This backend is very similar to `fuzzy_all_matches`, but instead of returning all matches above a certain confidence, it just returns the best one, regardless of how good it is.

In general, there's no reason to use this over `fuzzy_all_matches`, unless you have a specific scenario that means you always want a response, but can't be sure of a confidence level.

### Strict Regex (`will.backends.generation.strict_regex`)

Great for exact matches only.  If you only want your Will to do thing when it hears an exact command, or you have a bunch of different commands you're worried about getting mixed up in the fuzziness, `strict_regex` is the way for you to go.

This is the same behavior that was in Will 1.x and 0.x.

## Setting your backends

To set your generation backends, just update the following in `config.py`

```python
# Backends to generate possible actions, and metadata about them.
GENERATION_BACKENDS = [
    "will.backends.generation.fuzzy_all_matches",
    "will.backends.generation.strict_regex",
    # "will.backends.generation.fuzzy_best_match",
]
```


## Contributing a new backend

Writing a new generation backend is easy - just subclass `GenerationBackend`, and implement `do_generate`:

Note that the method should return a list of `GeneratedOption`s, including context, the backend name, and a score.


```python
from will.backends.generation.base import GenerationBackend, GeneratedOption


class MyGreatGenerationBackend(GenerationBackend):

    def do_generate(self, event):
        """Returns a list of GeneratedOptions"""
        matches = []

        message = event.data
        for name, l in self.bot.message_listeners.items():
            if this_is_a_perfect_match(message, l):
                o = GeneratedOption(context=context, backend="regex", score=100)
                matches.append(o)

        return matches

```

From there, just test it out, and when you're ready, submit a [pull request!](https://github.com/skoczen/will/pulls)

Now we've got a host of possible things Will can do and say.  It's time to look at how [Will decides what to do](/platform/execution).