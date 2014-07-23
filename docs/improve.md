# Making Will Better and Better

Will is built entirely on the shoulders of giants, and has a great community of developers that move it forward. He wouldn't exist without all of them.

We also welcome new contributions no matter how big or small.  Interested in contributing to will? We'd love to have you. Details below.


## Our Culture

Anyone is welcome to contribute to will, regardless of skill level or experience.  To make will the best he can be, we have one big, overriding cultural principle:

**Be kind.**

Simple.  Easy, right?

We've all been newbie coders, we've all had bad days, we've all been frustrated with libraries, we've all spoken a language we learned later in life.  In discussions with other coders, PRs, and CRs, we just give each the benefit of the doubt, listen well, and assume best intentions.  It's worked out fantastically.

This doesn't mean we don't have honest, spirited discussions about the direction to move will forward, or how to implement a feature.  We do.  We just respect one other while we do it.  Not so bad, right? :)


## Improve will's core

For big core features, you're probably best off opening an issue, and discussing it with one of the core developers *before* you hack your nights and weekends away.

Core changes to will are very much welcome.  In some cases, proposed changes have already been thought through, and there may be gotchas or sticking points we couldn't get past.  In other cases, it might be a direction we've purposely decided not to take will.  In most cases, we simply haven't thought of it, and would love the improvement! 

It's always great to get a heads up of what's coming down the pipe, and have an open dialog.  Thanks for reaching out and starting one!

In terms of the mechanics, you'll just want to:

1. Fork this repo.
2. Clone down a copy, set up redis and the env, as before.
3. Run `./start_dev_will.py` to start up just core will.

## Contribute new plugins

This one's pretty simple. Write good, clean code that does one thing well, document it properly, and submit a PR!

To submit a plugin that's running in your will,


1. Fork this repo.
2. Clone down a copy, set up redis and the env, as before.
3. Copy your plugin and docs over to the core will repo,
4. Run `./start_dev_will.py` to start up just core will, and test it out!


## Code standards and PRs

This one's hopefully straightforward:

- Incoming code should follow PEP8
- If you add new core-level features, please add documentation in the `docs` folder (we use mkdocs).  If you're not sure if they're needed, just ask!
- Please add your name and attribution to the AUTHORS file.
- Know you have our thanks for helping to make will even better!



## The Shoulders of Giants

Will leverages some fantastic libraries.  He wouldn't exist without them.

- [Bottle](http://bottlepy.org/docs/dev/) for http handling
- [Jinja](http://jinja.pocoo.org/) for templating
- [Sleekxmpp](http://sleekxmpp.com/) for listening to xmpp
- [natural](https://github.com/tehmaze/natural) and [parsedatetime](https://github.com/bear/parsedatetime) for natural date parsing
- [apscheduler](http://apscheduler.readthedocs.org/en/latest/) for scheduled task parsing
- [Requests](http://requests.readthedocs.org/en/latest/) to make http sane.

Will was originally written and is maintained by [Steven Skoczen](https://github.com/skoczen) at [GreenKahuna](https://www.greenkahuna.com).  The rest of the GK team has also pitched in, including [ckcollab](http://github.com/ckcollab), and [levithomason](http://github.com/levithomason).

Will's also has had help from lots of coders. Alphabetically:

- [adamgilman](https://github.com/adamgilman) gave you the friendly error messages when the hipchat key was invalid.
- [amckinley](https://github.com/amckinley) fixed a bug in the hipchat user list from missing params.
- [bfhenderson](https://github.com/bfhenderson) removed dependence on the v1 token, and made help more friendly.
- [crccheck](https://github.com/crccheck) gave you friendly error messages if your `WILL_ROOMS` was wrong.
- [dpoirier](https://github.com/dpoirier) figured out how to properly ignore the initial catch-up messages, and gave you log-level control.
- [jbeluch](http://github.com/jbeluch) found a bug with `get_roster` not populating in time.
- [michaeljoseph](https://github.com/michaeljoseph) suggested improvements to setup and requirements.txt format.
- [mrgrue](https://github.com/mrgrue) added support for the hipchat server beta.
- [netjunkie](https://github.com/netjunki) fixed a duplicated help module.
- [quixeybrian](https://github.com/quixeybrian) wrote the awesome new help system and stopped the rate limit nightmare.
- [rbp](https://github.com/rbp) added the `admin_only` argument, and fixed a bug with `room` not being passed along properly to messages.
- [tomokas](https://github.com/tomokas) fixed a bug in the `@randomly` decorator.

## Other Wills

If you're looking for plugin inspiration, here are some wills that are open-sourced:

- [GreenKahuna's will](https://github.com/greenkahuna/our-will)

**Note:** Have a will you've open-sourced? Please send it in a PR or Issue!  This list is tiny!

## Releases

#### 0.5.4 - July 22, 2014

* Upgrades bottle to 0.12.6 to fix [security bug](http://osvdb.org/show/osvdb/106526).


#### 0.5.3 - July 11, 2014

* `@randomly` functions now can run on the 59th minute, thanks to [https://github.com/tomokas](tomokas).
* Bad merge that duplicated `help.py` fixed by [https://github.com/netjunki](netjunki).
* "global name 'params' is not defined" bug fixed by [https://github.com/amckinley](amckinley).


#### 0.5.1 - July 2, 2014

* New `HIPCHAT_SERVER` setting to support [beta HipChat Server](https://www.hipchat.com/server), thanks to [mrgrue](https://github.com/mrgrue).


#### 0.5 Omnibus - June 27, 2014

* Big, big release, with backwards-incompatble changes.  Please read all the notes on this one!
* All-new config and environment setup, including an all-new `config.py` for plugin configuration, and all non-sensitive settings.
* Much, much improved bootstrapping code that validates settings, gives helpful output, and generally helps you get will running.
* Documentation!  Real-live documentation! 
* **Breaking**: `WILL_TOKEN` has been renamed `WILL_V1_TOKEN`.
* New `@require_settings` decorator for plugins to request validation that needed settings are present.
* Will now has a concept of modules (groups of plugins), and groups help output according.


#### 0.4.10 - June 6, 2014

* Brand-new `admin_only` argument to `hear()` and `respond_to()`, thanks to [rbp](https://github.com/rbp).  If a user is not in `WILL_ADMINS`, they won't be able to run any `admin_only=True` plugins.  Default for `WILL_ADMINS` is all users to retain backwards-compatibility.
* All commands in the `storage.py` plugin are now admin-only.
* `help` now only responds to direct asks, allowing other plugins to handle "help me with x", thanks to [bfhenderson](https://github.com/bfhenderson)


#### 0.4.9 - May 28, 2014

* Passing a `room` to a `.say()` now works properly, thanks to [rbp](https://github.com/rbp).
* New optional `WILL_LOGLEVEL` setting, thanks to [dpoirier](https://github.com/dpoirier).


#### 0.4.8 - May 21, 2014

* Will now ignores all previously sent messages properly, by passing in `bot` as the resource instead of an ugly time hack, thanks to [dpoirier](https://github.com/dpoirier).


#### 0.4.7 - May 15, 2014

* Will now prints a helpful message if one of your `WILL_ROOMS` is wrong, and continues starting, instead of crashing in a fiery ball, thanks to [crccheck](https://github.com/crccheck).


#### 0.4.6 - May 5, 2014

* `@route` decorators now honor all bottle arguments, most helpfully `method`! 


#### 0.4.5 - May 2, 2014

* Awesome new help system by [quixeybrian](https://github.com/quixeybrian).  
* "@will help" now only displays functions with docstrings, and formats them nicely.
* Old help (regexes and all) is available at "@will programmer help"


#### 0.4.4 - April 22, 2014

* Removes the dependence on the v1 token (though it still helps with rate-limiting), thanks to [bfhenderson](https://github.com/bfhenderson).
* Much friendlier error message on an invalid API key, thanks to [adamgilman](https://github.com/adamgilman).

#### 0.4.3 - ~ April 1, 2014

* Support for hundreds of users and rooms without hitting the API limit.
* `get_all_users` use of the bulk API [added](https://github.com/greenkahuna/will/pull/18) by [quixeybrian](https://github.com/quixeybrian).  Thanks also to [jbeluch](https://github.com/jbeluch) and [jdrukman](https://github.com/jdrukman) for nudges in the right direction.
* The start of some useful comments - the meat of will was hacked out by one person over a handful of days and it looks that way. Slowly but surely making this codebase more friendly to other contributions!
* Added a CONTRIBUTING.md file thanks to [michaeljoseph](https://github.com/michaeljoseph).
* Proper releases in the docs, and an updated `AUTHORS` file.  If you see something awry, send a PR!

#### 0.4 - ~ March 2014

* Ye olden past before we started keeping this list.  All contributions by GreenKahuna.  Will did everything that's not in the release list above.  That's called lazy retconning release lists!


- Make sure nothing from the readme is missed.

