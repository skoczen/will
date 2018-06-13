# Releases

#### 2.1.3 - June 13, 2018

Bugfix & feature release that includes:

Bugfixes: 
* Will is now robust against slack disconnects, and automatically handles reconnects, thanks to [https://github.com/Ashex](Ashex)!
* Will also now doesn't respond to every single message when he joins a new channel. Please send your thank-you cards to [https://github.com/Ashex](Ashex). 
* Makes will more robust at handling incorrect channel names in slack, thanks to [reist](https://github.com/reist).
* Properly renames `SLACK_DEFAULT_ROOM` to `SLACK_DEFAULT_CHANNEL` (with backwards-compatability) thanks (again!) to [reist](https://github.com/reist).
* Enable/disable backends from `generate_will_project` now properly puts the comment outside the strong.  Thanks to [phiro69](https://github.com/phiro69) for the report.


New features:
* Adds support for slack attachments, thanks to [https://github.com/Ashex](Ashex)
* Adds support for fabric v2, thanks to [reist](https://github.com/reist).
* Reminders now notify the person making the reminder, thanks to [unicolet](https://github.com/unicolet).
* `generate_will_project` now supports a `--backends` flag, thanks to [wontonst](https://github.com/wontonst).
* Will now explicitly notes if he's automagically using `REDIS_URL` to find the redis backend.

#### 2.1.2 - March 30, 2018

Bugfix release that includes:

* Fixes python 2 compatability (`str` instead of `basestring`) for the HipChat adapter, thanks to [wontonst](https://github.com/wontonst).


#### 2.1.1 - March 22, 2018

Bugfix release that includes:

* Fixes slack reconnect issues, thanks to [@mattcl](https://github.com/mattcl).  Props to [@cmachine](https://github.com/cmachine) for also submitting a fix.
* Saying "G" will no longer give you a picture of a pug, using the default settings. This is both tragic, and necessary. (Actual fix: adjusted default fuziness settings.  If you have the fuzzy backend on, and were seeing the rather hilarious/annoying [#327](https://github.com/skoczen/will/issues/327), set `FUZZY_MINIMUM_MATCH_CONFIDENCE = 91` in your config.py)
* Programmer help is working again, thanks to [@acommasplice](https://github.com/acommasplice).
* Fixes word game to work in python 3 thanks to [@netjunki](https://github.com/netjunki), and [ptomkiel-oktawave](https://github.com/ptomkiel-oktawave)'s report.
* Fixes up chat room rosters in HipChat with rosters > 1000 rooms, thanks to [@ostracon](https://github.com/ostracon)
* Fixes `get_room_from_message`, thanks to [@TaunoTinits](https://github.com/TaunoTinits)'s fix and  [ptomkiel-oktawave](https://github.com/ptomkiel-oktawave)'s report.
* Fixes an error that could occur on incoming webhooks on hipchat.  Thanks to [ptomkiel-oktawave](https://github.com/ptomkiel-oktawave) and others for a report.
* Fixes Will incorrectly talking to the main slack room, when he's directly addressed in 1-1 with something he doesn't know how to do.  Thanks to [netjunki](https://github.com/netjunki) for the report!


#### 2.1.0 - November 28, 2017

Planned release that includes:

* Automatic [docker hub builds](https://hub.docker.com/r/heywill/will/) thanks to [@mike-love](https://github.com/mike-love)
* Upgrades to use base markdownify package, as the proposed changes have been [merged and released](https://github.com/matthewwithanm/python-markdownify/pull/1).
* New fabric commands to manage docker builds and releases.


#### 2.0.2 - November 22, 2017

Bugfix release that fixes:

* Will once again joins all hipchat rooms `HIPCHAT_ROOMS` was not specified.  Thanks to [vissree](https://github.com/vissree) for finding and reporting this bug!

#### 2.0.1 - November 21, 2017

Same release as 2.0.1, removes beta tag.

#### 2.0.1beta4 - November 20, 2017

Bugfix release that fixes:

* `color` parameter wasn't working properly in Slack.
* Fixes up slack escaping, to support `<slack formatted|https://example.com>` links.  Thanks to [@netjunki](https://github.com/netjunki) for the report on this and the above.

Minor features:
* Adds a new `start_thread` parameter to `say()` and `reply()` to allow Will to start slack threads.


#### 2.0.1beta3 - November 13, 2017

Bugfix release that fixes:

* High CPU in some setups, thanks to [mattcl](https://github.com/mattcl) for the report and debuggging!
* Updates to `markdownify` fork 0.4.1.



#### 2.0.1beta2 - November 9, 2017

Bugfix release that fixes:

* Fixes `scheduled_say` breakage.
* Improves reminder plugins to capture and naturally handle "to"s, thanks to [wontonst](https://github.com/wontonst).
* Gets docker builds working, thanks to [mike-love](https://github.com/mike-love).


#### 2.0.1beta1 - November 7, 2017

**TL;DR: Slack, Rocket.chat, and Shell support, and you can write full chatterbots with Will now!**

This is a huge rewrite of will, adding pluggable backends for chat systems, Will's internal brains, pub-sub, and encryption.  

A huge number of really smart people gave their thoughts and suggestions throughout the process, not least [@hobson](https://github.com/hobson), [@woohgit](https://github.com/woohgit), [@netjunki](https://github.com/netjunki), [@sivy](https://github.com/sivy), [@antgel](https://github.com/antgel), [@shadow7412](https://github.com/shadow7412), [@brandonsturgeon](https://github.com/brandonsturgeon), [@pepedocs](https://github.com/pepedocs), [@tophsic](https://github.com/tophsic), and [@mike-love](https://github.com/mike-love).

Read all about what and why here: [What's new in Will 2](https://heywill.io/will2),

And when you're ready to upgrade, here's [the upgrade guide](http://skoczen.github.io/will/upgrading_to_2). (Spoiler: `pip install -U will`).

High-level, here's what's new:

- Slack support
- CLI/Shell backend
- [Rocket.chat](https://rocket.chat/) support, thanks to [antgel](https://github.com/antgel).
- Will's brains have been abstracted - you can now add custom [analysis](/backends/analysis), [generation](/backends/generation), and [execution](/backends/execution) backends to build everything from a straight regex-bot to a full chatterbot.
- [Pluggable I/O backends](/backends/io), which is how all of the above were done, and which means adding new platforms is pretty simple.
- [Pluggable storage](/backends/storage) backends.
- [Pluggable pubsub](/backends/pubsub) backends.
- Built-in encryption for storage and pub/sub (with [pluggable backends](/backends/encryption) as well.)
- Lots more intelligence around required settings and verification, to make first starting and debugging Will easier.
- Full Python 3 support. (Don't worry, 2.x [isn't going anywhere](https://heywill.io/will2#python3).)
- New `@will gif me` command.  Because it can't all be serious. :)


This release also changes a few bits of behavior, to be consistent:

- `self.reply()` *finally* no longer requires you to tediously pass the `message` back to it.  It's also smart, and backwards compatable with existing plugins.
- `admin_only` is explicitly flagged for deprecation and removal, to be replaced by the ACL system introduced in 2015 (largely, this is because having two different access control systems is crazy and painful.)  Switching is as easy as adding `ACL = {'admins': ['steven', 'will']}` to your config.py and find/replacing `admin_only=True` with `acl=['admins',] in your codebase.  For now, Will handles backwards compatibility by mapping the old settings into the new places, but he won't forever.  Thanks for updating, and making ongoing maintenence simpler!
- If no ACLs are specified and users try to perform restricted commands, they'll be allowed as before, but Will will complain to the console. A new `DISABLE_ACL` setting has been added to turn off the complaining.
- You can pass in `channel=` or `room=` when specifying a custom reply location.  If both are passed in, Will uses `channel`.

There are a couple *internal* backwards-incompatible changes:

- `RosterMixin` has been renamed `HipChatRosterMixin` and moved to `will.backends.io_adapters.hipchat`.  This change should not affect you unless you were specifically importing RosterMixin in your own plugins - everything in `WillPlugin` has been automatically routed to the right place, in a backwards-compatible way.
- `Room` and `RoomMixin` have similarly become `HipChatRoom` and `HipChatRoomMixin and moved to `will.backends.io_adapters.hipchat`.

As this is a *big* update, please report any bugs you see (no matter how small) to [the github issue tracker](https://github.com/skoczen/will/issues).  Thanks in advance for making Will even better!


#### 1.0.2 - October 24, 2017

Fixes and features in this release:

* Makes passing the `room=` option *much* easier (you can just use the room's name now,) thanks to [wontonst](https://github.com/wontonst).
* Adds support for jinja `custom_filters` in the `@rendered_template` decorator, thanks to [chillipeper](https://github.com/chillipeper).

#### 1.0.1 - October 10, 2017

Fixes and features in this release:

* Fixes what time plugin to not require World Weather's old API, thanks to [woohgit](https://github.com/woohgit).
* Adds Docker support, thanks to [mike-love](https://github.com/mike-love).
* Adds Python 3 support, thanks to [tenzer](https://github.com/tenzer).


#### 1.0.0 - September 29, 2017

**This is the end of major feature development for the hipchat-only version of Will.  Future development will be on 2.x, and while backwards compatability will be aimed for, it's not 100% guaranteed.**

Fixes and features in this release:

* Makes ACLs be case-insensitive, thanks to [woohgit](https://github.com/woohgit).
* Adds Hipchat card support, also thanks to [woohgit](https://github.com/woohgit).
* Gets Chatoms random topics working again, thanks to [bykof](https://github.com/bykof).
* Environment overrides for `PLUGINS` and `PLUGIN_BLACKLIST` (semicolon separated) are now possible, thanks to [mark-adams](https://github.com/mark-adams).

#### 0.9.5 - June 23, 2017

Quick bugfix release before the big changeover to 1.0, pluggable backends (Slack support), and more.

* Fixed: `@will image me` actually works again thanks to [antgel](https://github.com/antgel).


#### 0.9.4 - April 25, 2017

New releases and movement again!  Exciting things in the pipeline for will, and that's starting with a long-awaited release.  Thanks to everyone who both submitted code, and had saint-like patience with it being merged in.

* New: `self.append()` and `self.pop()` methods to support list storage, thanks to [woohgit](https://github.com/woohgit).
* Fixed: `@will image me` works again (but requires a google API key - see `config.py`, thanks to [shadow7412](https://github.com/shadow7412).
* Fixed: `@will pugs` thankfully works again, thanks to [gordol](https://github.com/gordol).
* Improvement: `@will help <plugin>` now gives plugin-specific help, thanks to [tophsic](https://github.com/tophsic).
* Improvement: Blacklisted modules aren't even attempted to be imported, thanks to [BrianGallew](https://github.com/BrianGallew).
* Improvement: File storage engine expires properly, thanks to [BrianGallew](https://github.com/BrianGallew).
* Improvement: Zombie users no longer cause will trouble, thanks to [BrianGallew](https://github.com/BrianGallew).
* Improvement: Will now no longer gets stuck if organizations have more than 2000(!) hipchat rooms, courtesy of [woparry](https://github.com/woparry) and [danbourke](https://github.com/danbourke).
* Improvement: V2 API calls for multiple rooms now properly uses `max-results` and doesn't hang, thanks to [chillipeper](https://github.com/chillipeper).
* Improvement: Much-improved test runners, and proper case for Bitbucket, thanks to [mark-adams](https://github.com/mark-adams).
* Improvement: `_available_rooms` is now populated with `Room` objects, regardless of whether you use V1 or V2, thanks to [jcdyer](https://github.com/jcdyer).
* Improvement: Output logging now includes timestamps by default, thanks to [pepedocs](https://github.com/pepedocs).
* Improvement: Upgraded to `hiredis` > 0.2 to get windows builds working, thanks to [Regner](https://github.com/Regner).
* Improvement: Updated to the new pagerduty docs, thanks to [woohgit](https://github.com/woohgit).
* Improvement: Generation script doesn't make a duplicate `hi` response, thanks to [brandonsturgeon](https://github.com/brandonsturgeon) and [derek-adair](https://github.com/derek-adair).


#### 0.9.3 - September 11, 2015

Thanks for your patience on this long-delayed release!  Here's what's new:

* New: Will watches bitbucket, and alerts on downtime, thanks to [mvanbaak](https://github.com/mvanbaak).
* New: `@will urban dictionary ______`, thanks to [Ironykins](https://github.com/Ironykins).
* New: 1-1 messages now support HTML, thanks to [AndrewBurdyug](https://github.com/AndrewBurdyug) and [brandonsturgeon](https://github.com/brandonsturgeon)
* Improvement: Batch-getting of rooms, thanks to [charlax](https://github.com/charlax).
* Improvement: Better handling of uptime check edge cases, thanks to [woohgit](https://github.com/woohgit).
* Improvement: Proper docs for installing redis on ubuntu/debian, thanks to [kenden](https://github.com/kenden).
* Improvement: Pulled an extraneous doc page, thanks to [woohgit](https://github.com/woohgit).
* Improvement: Fixes to the route doc syntax, thanks to [brandonsturgeon](https://github.com/brandonsturgeon).
* Improvement: Docs now fit the new mkdocs format, thanks to [d0ugal](https://github.com/d0ugal).
* Improvement: New travis.yml setup for easier travis running, and plugged my CircleCI builds into the github repo. All future PRs should automatically have tests run!

#### 0.9.2 - June 5, 2015

* Fixes bug that caused will not to join all rooms if `ROOMS` was missing. Thanks to [camilonova](https://github.com/camilonova) for the report!

#### 0.9.1 - May 30, 2015

* Fixes bug that affected `@will`s - thanks to [woohgit](https://github.com/woohgit) for the report!

#### 0.9 - May 29, 2015

* **BREAKING:** Module change. New `will.plugins.fun` module. Existing will installs will need to add it to your `config.py` to keep the fun!
* New:  Support for Pagerduty workflows, thanks to [woohgit](https://github.com/woohgit). This is really tremendous stuff. [Check out the docs here](plugins/bundled.md#pagerduty-integration)!
* New: [Pluggable storage backends](deploy.md#storage-backends), with support for couchbase and local file storage, in addition to redis.  Many thanks to [borgstrom](https://github.com/borgstrom)
* New: [ACL](plugins/builtins.md#access-control) functionality, thanks to [woohgit](https://github.com/woohgit).  Backwards-compatable, even!
* New: Made will a little more fun, thanks to [camilonova](http://github.com/camilonova).  Hint: it involves the world's most meme-friendly dog.
* New: Will can now construct google poems, thanks to [AirbornePorcine](https://github.com/AirbornePorcine). Truly, his creativity knows no bounds.
* Improvement: Moved stuff like that into a new "fun" module.  Dry, anti-fun people can now disable it more easily. ;)
* Improvement: "What time is it" now outputs time zones, thanks to [woohgit](https://github.com/woohgit).
* Improvement: No more rate-limit problems on the v2 token, thanks to [grundprinzip](https://github.com/grundprinzip).
* Improvement: Messages are now `.strip()`ed before being compared, to handle [frozen-fingered-typos](https://github.com/skoczen/will/pull/145).  Thanks, [woohgit](https://github.com/woohgit)!
* Fix: Typo in the docs gone.  Thanks, [woohgit](https://github.com/woohgit).
* Fix: Bugs in proxy support are fixed, thanks to [dmuntean](https://github.com/dmuntean).


#### 0.8.2 - April 24, 2015

* Fixes an odd remaining bug with `@randomly`, thanks to [camilonova](https://github.com/camilonova)'s continued debugging.

#### 0.8.1 - April 23, 2015

* Moves `version` plugin into admin, so it just works for most users.

#### 0.8 - April 23, 2015

* What happens when life gets busy and we go a full month and a half between will releases?  Lots and lots:
* New: All-new `@will who is in this room?` command, thanks to [puug](https://github.com/puug).
* New: Will now can shorten links via bitly `@will bitly http://example.com`, thanks to [keNzi](https://github.com/keNzi).
* New: Will now supports a `PROXY_URL` setting, for getting around funky firewalls, thanks to [dmuntean](https://github.com/dmuntean).
* New: `@will version` command to check version number, thanks to [woohgit](https://github.com/woohgit).
* New: Awesome new `remind ___ to ___ at ___`, thanks to [woohgit](https://github.com/woohgit).
* New: Will now keeps an eye on hipchat's uptime as well, thanks to [netjunki](https://github.com/netjunki).
* Fix: a breaking bug in the `@randomly` decorator, thanks to a report by [camilonova](https://github.com/camilonova).
* Support: Handles a breaking change in the hipchat API, thanks to [brandonsturgeon](https://github.com/brandonsturgeon).
* Support: Updates to v2 of the underquoted API, thanks [jessamynsmith](https://github.com/jessamynsmith).
* Support: Updated to the new WorldWeatherOnline endpoint, since they had DDOS problems, thanks to [woohgit](https://github.com/woohgit).
* Improvement: The most important kind of PRs.  Spelling fixes.  Many thanks to [jquast](https://github.com/jquast).
* Improvement: `self.save()` now accepts an `expire` value, thanks to [netjunki](https://github.com/netjunki).
* Improvement: PEP8 passes for the whole codebase, with flake8 added to automated tests.

#### 0.7.3 - March 3, 2015

* Fixed a breaking bug to world time, thanks to [woohgit](https://github.com/woohgit).

#### 0.7.2 - February 27, 2015

* Improved handling when `.reply()` is called incorrectly, thanks to a report by [dothak](https://github.com/dothak)
* Fixed the [annoying](https://github.com/skoczen/will/issues/78) "github's ok" on first launch.
* Restored Python 2.6 compatability thanks to the report and patience of [JPerkster](https://github.com/JPerkster).
* Lots of code cleanup toward pep8.

#### 0.7.1 - February 5, 2015

* Improved talkbackbot regex, suggested by [PrideRage](https://github.com/PrideRage).


#### 0.7.0 - February 4, 2015

* Adds a port of the awesome [talkbackbot](https://github.com/jessamynsmith), thanks to [jessamynsmith](https://github.com/jessamynsmith), who super-kindly ported it at my request!
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
* **Breaking**: `WILL_TOKEN` has been renamed `WILL_HIPCHAT_V1_TOKEN`.
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

