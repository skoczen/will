Last Update: May 5, 2017

## A Note from Steven

> "Open source projects with no funding mechanism typically stagnate and die." 
-[GreenSock](https://greensock.com/why-license)

I read that quote a few years ago when considering using GreenSock in a front-end product, and it stuck with me since, in both Will and my other projects.  At first, the statement really bugged me - but as I looked objectively at my own long list of abandoned open-source work, I realized there was a deep truth to it.

Will has gone on a similar journey - it was written with the support from a couple of my day jobs, and after those left, my time dried up, and the project started to stagnate.

That stagnation has bugged me for a long time, but I didn't really have a way to solve the problem until now.

What this document outlines is a future roadmap for Will that's both open-source and revenue-generating.  A project that can keep the codebase active, healthy, and adding new features (First up: Slack), while also paying my (and hopefully other folks') bills - and with some luck, maybe even changing the world.

I recognize that a lot of people have contributed to will, and while many of you will be thrilled by the prospect of active, sustainable development, a few folks might have the "OMG WHAT KIND OF SELL OUT BULL*** IS THIS??!?!".   To those folks, I'd like to reiterate - Will is open-source, and is going to stay that way. :) 

Now let's talk about how.

_Note_: I use the royal "we" below because it feels more natural in the long-term.  Right now it's just me and it's awkward.  Thanks for rolling with it.


## Overall Project Structure and Goals

Will is being founded as a company, and with the core chat bot product, we'll have both the open-source library and a PaaS/SaaS service (ala Wordpress.com/.org).  The core of the company is around an idea we call Personal AI.

(Read more about the mission at [http://heywill.io/mission](http://heywill.nz/mission).)

This shift means growing the project to something much bigger than a hipchat bot, and into a write-once, run anywhere platform for chat bots, AIs, and fun new holy-crap-that's-amazing ideas.

The big goal is to provide an easy-to-build-on batteries-included platform that bridges modes of communication (HipChat, Slack, SMS, Email, Telegram, FB Messenger, etc) with services (IFTTT, Amazon AI, IBM Watson, Google APIs, etc) and built-in AI tools (NLP, ML, DL, etc).  

This broader platform serves as an OS for AI development, and has the tremendously creative working name of AIOS.

Developers can build AIOS apps (our current plugins) for will using any and all of those tools, and run them on their personal wills or distribute them to a broader audience.

Will the company will focus, like Wordpress, on running the PaaS and SaaS platforms, and a marketplace for apps.  Our goal is to keep Will development brisk, bring in talented folks across the spectrum, and keep Will available to anyone, anywhere on the planet, regardless of financial or technical access. 


## Project Roadmap

Here's the nuts and bolts of how, today, we see this rolling out.

0.9.4 - Just released, catches up almost all open PRs

1.0 - Soon, closes up existing issues, code cleanup and prep for improvements

1.2 - Slack Support, `IOBackend` documented and working.  PRs for new IOs accepted.

1.3 - API Support released, via an `APIBackend` implementation of `IOBackend`.

1.4 - IFTTT Support, `SkillsBackend` documented and working.  PRs for new Skills accepted.

1.5 - Will UI, with on-the-fly config, plugin enable/disable, and restartability.

1.6 - App specs for AIOS and `AIOSApp` class released.

1.7 - Release of first five apps. TBD, but considered: (Image me, Remind me, Groceries, News Summary, Word Game, Stale Package Finder)

2.0 - App Marketplace released, Git library integration released, and all existing Will plugins released as AIOS apps.

2.0+ - "The root of all evil is premature optimization."  Releases after 2.0 are likely to move in a direction of improved AIOS features, more built-in AI tools, smarter and richer message processing and context, cross-app communication, and speed/reliability bumps.  We'd also like to look at the feasibility of authoring apps in both Python and JS.  

That said, this will really be determined after 2.0 is released, the launch craziness settles down, and we hear from the community and customers which directions need the most support, and what pain points folks are feeling the most.

We can't wait to have those discussions.

## Release Schedule.

A new version of Will will be released on the 1st of every month, with a 12-month guarantee for `IOBackend`, `SkillsBackend`, API and AIOS APK function stability, and a minimum 6 month deprecation warning.

## Questions and Comments

I've set up an issue [here](https://github.com/skoczen/will/issues/257) to talk through this new direction, hear people's thoughts, comments, suggestions, and feedback.

I'm so excited to take will in this new, bigger direction, find consistent time and energy to keep him maintained, and grow him into something amazing together.

Thank you so much for contributing to will thus far, and I can't wait to see where we take him together!

-Steven