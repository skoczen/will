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

- [Bottle](http://bottlepy.org/docs/dev/) for http handling,
- [Jinja](http://jinja.pocoo.org/) for templating,
- [Sleekxmpp](http://sleekxmpp.com/) for listening to xmpp,
- [natural](https://github.com/tehmaze/natural) and [parsedatetime](https://github.com/bear/parsedatetime) for natural date parsing,
- [apscheduler](http://apscheduler.readthedocs.org/en/latest/) for scheduled task parsing,
- [Requests](http://requests.readthedocs.org/en/latest/) to make http sane.

Will was originally written and is maintained by [Steven Skoczen](https://github.com/skoczen) at [GreenKahuna](https://www.greenkahuna.com).  The rest of the GK team has also pitched in, including [ckcollab](http://github.com/ckcollab), and [levithomason](http://github.com/levithomason).

Will's also has had help from lots of coders. Alphabetically:

- [adamcin](https://github.com/adamcin) gave you html support in 1-1 chats, using the new v2 API, and made bootstrapping more reliable.
- [adamgilman](https://github.com/adamgilman) gave you the friendly error messages when the hipchat key was invalid.
- [amckinley](https://github.com/amckinley) fixed a bug in the hipchat user list from missing params.
- [bfhenderson](https://github.com/bfhenderson) removed dependence on the v1 token, and made help more friendly.
- [bsvetchine](https://github.com/bsvetchine) fixed a bug with README generation.
- [carsongee](https://github.com/carsongee) pooled your redis connections.
- [crccheck](https://github.com/crccheck) gave you friendly error messages if your `WILL_ROOMS` was wrong.
- [dpoirier](https://github.com/dpoirier) figured out how to properly ignore the initial catch-up messages, and gave you log-level control.
- [jbeluch](http://github.com/jbeluch) found a bug with `get_roster` not populating in time.
- [jessamynsmith](jessamynsmith) was kind enough to port [talkbackbot](https://github.com/jessamynsmith) over, at my request.
- [hobson](http://github.com/hobson) made setup.py more robust across operating systems, and improved the docs.
- [neronmoon](https://github.com/neronmoon) made it easier to mention will with non-standard case
- [michaeljoseph](https://github.com/michaeljoseph) suggested improvements to setup and requirements.txt format.
- [mrgrue](https://github.com/mrgrue) added support for the hipchat server beta.
- [netjunkie](https://github.com/netjunki) fixed a duplicated help module.
- [pcurry](https://github.com/pcurry) added travis support.
- [PrideRage](https://github.com/PrideRage) gave you access to a room's entire history.
- [quixeybrian](https://github.com/quixeybrian) wrote the awesome new help system and stopped the rate limit nightmare.
- [rbp](https://github.com/rbp) added the `admin_only` argument, and fixed a bug with `room` not being passed along properly to messages.
- [sivy](https://github.com/sivy) added a config flag for disabling SSL, and the ability to look up a user by nickname.
- [tomokas](https://github.com/tomokas) fixed a bug in the `@randomly` decorator.
- [wohali](https://github.com/wohali) tracked down the annoying DNS thread issue, and got will on the right path.
- [woohgit](https://github.com/woohgit) added support for the v2 WorldWeatherOnline API.

## Other Wills

If you're looking for plugin inspiration, here are some wills that are open-sourced:

- [BuddyUp's will](https://github.com/buddyup/our-will)
- [GreenKahuna's will](https://github.com/greenkahuna/our-will)

**Note:** Have a will you've open-sourced? Please send it in a PR or Issue!  This list is tiny!

## Releases

#### 0.7.0 - February 4, 2015

* Adds a port of the awesome [talkbackbot](https://github.com/jessamynsmith), thanks to [jessamynsmith](jessamynsmith), who super-kindly ported it at my request!
* Oh, yeah. That port also includes the first proper tests in will, and a pretty solid pattern for testing plugins.  Woo!  More huge thanks to [jessamynsmith](https://github.com/jessamynsmith).


#### 0.6.9 - January 30, 2015

* Fixed copypasta error caught by the keen eye of [dpoirier](https://github.com/dpoirier).

#### 0.6.8 - January 30, 2015

* Will now supports templates directories within plugins.  Just put a `templates` directory in the plugin's module, and it will be detected.  Thanks to [sivy](https://github.com/sivy) for the idea and willingness to get it done!


#### 0.6.7 - January 29, 2015

* Addition of `.get_user_by_nick()` method, to look up users by nick, thanks to [sivy](https://github.com/sivy).
* Bugfix to `ALLOW_INSECURE_HIPCHAT_SERVER` when specified in `config.py`, thanks to [sivy](https://github.com/sivy).

#### 0.6.6 - January 29, 2015

* New `room.history` attribute with a room's history, thanks to [PrideRage](https://github.com/PrideRage)
* New setting: `ALLOW_INSECURE_HIPCHAT_SERVER`, which will disable SSL checks (you're on your own), thanks to [sivy](https://github.com/sivy).
* Adds support for V2 of the WorldWeatherOnline API (used for world times, weather) thanks to [woohgit](https://github.com/woohgit).
* Adds new release and doc deploy scripts, so the github [releases](https://github.com/skoczen/will/releases) are kept up to date.  Thanks to [crccheck](https://github.com/crccheck) for noticing and reporting they were stale!


#### 0.6.5 - January 23, 2015

* Removes mkdocs from the production requirements.txt to fix a Jinja version problem.  Thanks to the report from [PrideRage](https://github.com/PrideRage).

#### 0.6.4 - January 19, 2015

* Switches to bottle to cherrypy over gevent, which should solve lingering gevent DNS threading issues, thanks to [wohali](https://github.com/wohali).
* Support for @will, @WILL, @wIll, thanks to [neronmoon](https://github.com/neronmoon)


#### 0.6.3 - December 30, 2014

* Better error handling for weirdly formatted messages. 
* Better generated README, thanks to [bsvetchine](https://github.com/bsvetchine).


#### 0.6.2 - September 23, 2014

* Bugfix on `generate_will_project`, thanks to the report by [MattyDub](https://github.com/MattyDub).


#### 0.6.1 - September 23, 2014

* Freezes apscheduler to < 3.0, since its API was backwards incompatibile.


#### 0.6.0 - September 17, 2014

* Methods in a single class now share a common instance, thanks to [amckinley](https://github.com/amckinley).
* Redis connections are now pooled (which should help with "max clients exceeded" errors), thanks to [carsongee](https://github.com/carsongee).
* Preliminary travis ci support, thanks to [pcurry](https://github.com/pcurry).
* More gramatically correct documentation by [hobson](https://github.com/hobson).


#### 0.5.7 - September 3, 2014

* Improvements to setup.py to be robust a variety of linux/unixes by [hobson](https://github.com/hobson).


#### 0.5.6 - August 26, 2014

* Fix for 1-1 bootstrapping bug, thanks to [adamcin](https://github.com/adamcin).


#### 0.5.5 - August 25, 2014

* Full html support in 1-1 chats, thanks to [adamcin](https://github.com/adamcin).


#### 0.5.4 - July 22, 2014

* Upgrades bottle to 0.12.6 to fix [security bug](http://osvdb.org/show/osvdb/106526).


#### 0.5.3 - July 11, 2014

* `@randomly` functions now can run on the 59th minute, thanks to [tomokas](https://github.com/tomokas).
* Bad merge that duplicated `help.py` fixed by [netjunki](https://github.com/netjunki).
* "global name 'params' is not defined" bug fixed by [amckinley](https://github.com/amckinley).


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

