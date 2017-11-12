<h1>Upgrading to Will 2.0</h1>

Will was born four years ago, and 0.x and 1.x lived long, good lives.

But as the years passed, there were increasing concerns about HipChat lock-in, and it was time to make Will smarter.  

So six months ago, work on Will 2.0 began, and today it's finally here! All of our Wills are free from lock-in, future-proofed, and whole lot smarter.  If you're just hearing about this, it's worth a quick read of the [release announcement](https://heywill.io/will2) for a bit more context!

# The Short Version: Just pip install
While Will has picked up a bunch of features and improvements in 2.0, we've aimed to keep him backwards-compatable with 1.x and 0.x releases.  If you weren't using any undocumented internal methods and you're already using redis, upgrading should be as easy as:

```shell
pip install --upgrade will
```

From there, you can just `./run_will.py`, and things should Just Work.

You will, however, see a lot of output from Will, telling you that some names have changed, and asking you to update them in your `config.py` when you have time.  You can either just follow those instructions, or the guide below.

# The Long Version:

### 1. Add IO backends.

If you're planning to continue only using HipChat (until it's replaced by Stride), we'd recommend that you add this to your `config.py`:

```python
IO_BACKENDS = [
    "will.backends.io_adapters.hipchat",
    "will.backends.io_adapters.shell",
    # "will.backends.io_adapters.slack",
    # "will.backends.io_adapters.rocketchat",
]
```

That will enable the HipChat and local shell stdin/stdout backend, for easy testing. 

If you want to also bring your Will into a Slack or Rocket.Chat room in the future, just uncomment that backend and restart!

### 2. Update the HipChat tokens to be namespaced.  

You'll see this starting up, but when you have time, update your tokens as follows:  
(If you're using `WILL_` environment variables, please add the `WILL_` as needed:)

- `USERNAME` becomes `HIPCHAT_USERNAME`
- `TOKEN` or `V1_TOKEN` become `HIPCHAT_V1_TOKEN`
- `V2_TOKEN` becomes `HIPCHAT_V2_TOKEN`
- `DEFAULT_ROOM` becomes `HIPCHAT_DEFAULT_ROOM`
- `HANDLE` should be removed, as it's now pulled live from the HipChat servers and not used.
- `NAME` should be removed, as it's now pulled live from the HipChat servers and not used.
- `PASSWORD` becomes `HIPCHAT_PASSWORD`
- `ROOMS` becomes `HIPCHAT_ROOMS`


### 3. Set up Redis

At the moment, Redis is the only working pubsub backend, and is required to run Will. So, if you're not already running it, you'll need it for 2.x.

If this is impossible for your setup, ZeroMQ support is in the works, and we're looking to add a pure-python backend as well in 2.1 or 2.2.  Creating a new pubsub backend just requires subclassing `BasePubSub` and implementing four methods - so if someone has a little time to bring those along, a pull request is welcome!


### 4. Set your encryption secret key.

Will now encrypts all messages on the pubsub wire and in storage by default.  Without a `SECRET_KEY` set, he'll auto-generate one based on the machine MAC address, but this isn't a perfect solution, and will mean that he can't access his storage if there are hardware changes (or he's running in a virtualized environment that has shifting MACs.)

Please set `SECRET_KEY` as soon as possible.

The recommended way is to set it as an environmental variable, `WILL_SECRET_KEY`, in an environment that is secured and you trust.  Any string will work, and entropy is good. 


### 5. Set the new 2.0 settings to your liking.

Will 2 ships with bunch of new features, and though we've provided sensible defaults, if you'd like, you can update your `config.py` with your preferences.

The simplest way to see everything is to have Will generate a `config.py.dist` that you can use for comparison:

```shell
$ generate_will_project --config-dist-only
...
Created a config.py.dist.  Open it up to see what's new!
```

It's worth reading through the new `config.py`, but here's a few areas specifically worth a look:

### Platform and Decision-making

As mentioned above, there are now multiple IO backends and platforms that Will can communicate on. It's also now easy to [write your own](/backends/io), pull requests are very welcome, and more are coming soon.  Here's all the options:

```python
IO_BACKENDS = [
    "will.backends.io_adapters.slack",
    "will.backends.io_adapters.hipchat",
    "will.backends.io_adapters.rocketchat",
    "will.backends.io_adapters.shell",
]
```


Will 2 also comes with pluggable brains - split into Analysis, Generation, and Execution backends.  The defaults are solid and behave similarly to Will 1.0 (the only difference is a high-confidence fuzzy matching engine), but if you're interested in making your Will more flexible, or adding more context to his responses, building [custom backends is easy](/backends/analysis).

Here's all of the options, with the defaults uncommented.   It's worth pulling this into your `config.py`.

```python
# Backends to analyze messages and generate useful metadata
ANALYZE_BACKENDS = [
    "will.backends.analysis.nothing",
    "will.backends.analysis.history",
]

# Backends to generate possible actions, and metadata about them.
GENERATION_BACKENDS = [
    "will.backends.generation.strict_regex",
    "will.backends.generation.fuzzy_all_matches",
    # "will.backends.generation.fuzzy_best_match",
]

# The "decision making" backends that look among the generated choices,
# and decide which to follow. Backends are executed in order, and any
# backend can stop further evaluation.
EXECUTION_BACKENDS = [
    "will.backends.execution.best_score",
    # "will.backends.execution.all",
]
```

There are also a few settings to tweak things like the fuzzy logic.  These have sensible defaults, but you can tweak them to your liking.

```python
# Confidence fuzzy generation backends require before Will responds
# https://pypi.python.org/pypi/fuzzywuzzy
FUZZY_MINIMUM_MATCH_CONFIDENCE = 90  # Defaults to 90%
FUZZY_REGEX_ALLOWABLE_ERRORS = 3
```

### 6. That's it - let us know how it goes!

That's all you really need to know to flip the switch to Will 2.0.  

As there's a lot of new stuff in this release, it's possible that some bugs have slipped through the cracks.  Please submit anything you find, no matter how small, [into the github issue tracker](https://github.com/skoczen/will/issues).  We'll be active in fixing things ASAP and helping if you're stuck.

Thanks for using Will, and for going through the big upgrade!  We're excited about what the future holds, and happy to get your bots free from platform lock-in.

If you'd like to do a deeper dive into what's new, check out the documentation [on Will's new brain](/backends/overall/).