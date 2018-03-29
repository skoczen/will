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
3. `pip install -r requirements.dev.txt`
4. Copy your plugin and docs over to the core will repo,
5. Run `./start_dev_will.py` to start up just core will, and test it out!


## Code standards and PRs

This one's hopefully straightforward:

- Incoming code should follow PEP8
- If you add new core-level features, please add documentation in the `docs` folder (we use mkdocs).  If you're not sure if they're needed, just ask!
- Please add your name and attribution to the AUTHORS file.
- Know you have our thanks for helping to make will even better!


## Tests

Shamefully, tests are just getting rolling, and a proper, well-architected test harness is in the works. However, there are *some* tests you can run by running:

```bash
tox
```

More soon!


## The Shoulders of Giants

Will leverages some fantastic libraries.  He wouldn't exist without them.

- [Bottle](http://bottlepy.org/docs/dev/) for http handling,
- [Jinja](http://jinja.pocoo.org/) for templating,
- [Sleekxmpp](http://sleekxmpp.com/) for listening to xmpp,
- [natural](https://github.com/tehmaze/natural) and [parsedatetime](https://github.com/bear/parsedatetime) for natural date parsing,
- [apscheduler](http://apscheduler.readthedocs.org/en/latest/) for scheduled task parsing,
- [Requests](http://requests.readthedocs.org/en/latest/) to make http sane.

Will was originally written and is maintained by [Steven Skoczen](http://stevenskoczen.com).  Credit to GreenKahuna (now defunct) and [BuddyUp](http://www.buddyup.org) for supporting those efforts with on-the-job time.

Will's also has had help from lots of coders. Alphabetically:

- [acommasplice](https://github.com/acommasplice) fixed up the programmer help, so it works again.
- [adamcin](https://github.com/adamcin) gave you html support in 1-1 chats, using the new v2 API, and made bootstrapping more reliable.
- [adamgilman](https://github.com/adamgilman) gave you the friendly error messages when the hipchat key was invalid.
- [antgel](https://github.com/antgel) fixed the image plugin, for reals and added awesome documentation.
- [amckinley](https://github.com/amckinley) fixed a bug in the hipchat user list from missing params.
- [bfhenderson](https://github.com/bfhenderson) removed dependence on the v1 token, and made help more friendly.
- [borgstrom](https://github.com/borgstrom) gave you beautifully architected storage backends, including support for couchbase and local storage.
- [brandonsturgeon](https://github.com/brandonsturgeon) jumped on hipchat's API-breaking change, and made will immune in a flash.  Improved the docs all over, too.
- [BrianGallew](https://github.com/BrianGallew) improved the blacklist import mechanism, so blacklisted modules aren't even attempted to be imported, taught will to handle zombie users with grace, and fixed the file storage backend.
- [bsvetchine](https://github.com/bsvetchine) fixed a bug with README generation.
- [buran](https://github.com/AndrewBurdyug) added HTML support to 1-1 messages.
- [carsongee](https://github.com/carsongee) pooled your redis connections.
- [camilonova](https://github.com/camilonova) fixed the `@randomly` decorator, and brought the joy of more pugs to your life.  He's also reported several important bugs.
- [ckcollab](http://github.com/ckcollab) was one of the original contributors, when will was first built at GreenKahuna.
- [charlax](https://github.com/charlax) gave us batch-get of rooms via the V2 API.
- [chillipeper](https://github.com/chillipeper) fixed up the max-size and handling of V2 rooms, and taught will how to use bottle's `custom_filters`.
- [crccheck](https://github.com/crccheck) gave you friendly error messages if your `WILL_ROOMS` was wrong.
- [d0ugal](https://github.com/d0ugal) fixed up the docs to meet the new mkdocs standard.
- [danbourke](https://github.com/danbourke) submitted a fix for the >2000 rooms bug, and kept Will happy.
- [derek-adair](https://github.com/derek-adair) found a solution for the duplicated 'hi' messages.
- [dpoirier](https://github.com/dpoirier) figured out how to properly ignore the initial catch-up messages, and gave you log-level control.
- [dmuntean](https://github.com/dmuntean) gave you proxy support, and kept it working..
- [hobson](http://github.com/hobson) made setup.py more robust across operating systems, and improved the docs.
- [Ironykins](https://github.com/Ironykins) brought you urban dictionary support.
- [kenden](https://github.com/kenden) fixed up the redis docs for ubuntu/debian.
- [jbeluch](http://github.com/jbeluch) found a bug with `get_roster` not populating in time.
- [jcdyer](https://github.com/jcdyer) made the `_available_rooms` object consistent across API versions.
- [jessamynsmith](https://github.com/jessamynsmith) was kind enough to port [talkbackbot](https://github.com/jessamynsmith) over, at my request, then kept it updated through version changes.
- [jquast](https://github.com/jquast) did the noble and oft unappreciated work of spelling fixes.
- [keNzi](https://github.com/keNzej) added shorten url function using bitly service.
- [levithomason](http://github.com/levithomason) was one of the original contributors, when will was first built at GreenKahuna.
- [mark-adams](https://github.com/mark-adams) cleaned up a Bitbucket typo.
- [mattcl](https://github.com/mattcl) taught will to reconnect to Slack when hiccups occur.
- [mike-love](https://github.com/mike-love) added Docker support to make running Will easier - and then re-updated it to support Will 2.x!
- [hobson](http://github.com/hobson) made setup.py more robust across operating systems, and improved the docs.
- [neronmoon](https://github.com/neronmoon) made it easier to mention will with non-standard case
- [michaeljoseph](https://github.com/michaeljoseph) suggested improvements to setup and requirements.txt format.
- [mrgrue](https://github.com/mrgrue) added support for the hipchat server beta.
- [mvanbaak](https://github.com/mvanbaak) brought you support for bitbucket uptime.
- [netjunkie](https://github.com/netjunki) fixed a duplicated help module, added an expire parameter to `self.save()`, added support for will watching hipchat's status, fixed some redis config bugs, and kept word game working on py3.
- [ostracon](https://github.com/ostracon) got chat room replies working for orgs with > 1000 rooms.
- [pcurry](https://github.com/pcurry) added travis support.
- [pepedocs](https://github.com/pepedocs) added friendly timestamps to the default logging output.
- [PrideRage](https://github.com/PrideRage) gave you access to a room's entire history, and suggested a better talkback regex.
- [quixeybrian](https://github.com/quixeybrian) wrote the awesome new help system and stopped the rate limit nightmare.
- [Regner](https://github.com/Regner) upgraded the hiredis version to work on windows.
- [rbp](https://github.com/rbp) added the `admin_only` argument, and fixed a bug with `room` not being passed along properly to messages.
- [shadow7412](https://github/shadow7412) cleaned up a bunch of regex, and fixed up `image me` after google pulled the free API.
- [sivy](https://github.com/sivy) added a config flag for disabling SSL, and the ability to look up a user by nickname.
- [tenzer](https://github.com/tenzer) added python 3 support!
- [tomokas](https://github.com/tomokas) fixed a bug in the `@randomly` decorator.
- [tophsic](https://github.com/tophsic) made help friendlier, including plugin-specific help.
- [@TaunoTinits](https://github.com/TaunoTinits) fixed the `get_room_from_message` method in 2.x.
- [wohali](https://github.com/wohali) tracked down the annoying DNS thread issue, and got will on the right path.
- [woohgit](https://github.com/woohgit) added support for the v2 WorldWeatherOnline API, and fixed it when I broke it, and then fixed it again when they changed their endpoint.  He also taught will how to say his version number.  And `remind ___ to ___ at ___`.  Awesome. And fixed lots of docs.  And put the time zone with "what time is it?".  And then added an entire Pagerduty workflow.  And made message parsing more reliable.  And wrote the ACL support.  And even more doc fixes. And improvements on uptime monitoring edge cases. And kept Pagerduty working. And added `append` and `pop` list support. And ditched WorldWeatherOnline when it started to hurt. Yep.
- [wontonst](https://github.com/wontonst) made it simple to have will reply to a specific room, made reminders more friendly, and kept py2/3 compatability working on HipChat.
- [woparry](https://github.com/woparry) made sure that Will could handle organizations with a massive (>2000) number of rooms.


## Other Wills

If you're looking for plugin inspiration, here are some wills that are open-sourced:

- [BuddyUp's will](https://github.com/buddyup/our-will)
- [Skoczen's will](https://github.com/skoczen/my-will)
- [edX's devops will](https://github.com/edx/alton)
- [edX's fun will](https://github.com/edx/xsy)

**Note:** Have a will you've open-sourced? Please send it in a PR or Issue!  This list is tiny!


Curious how Will's grown over the years?  [Check out the releases](/releases)!