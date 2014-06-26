# Teach your will awesome stuff, easily

Your will is all yours.  He'll come with all the great functions of the will library, but the power to teach him the things that are really useful to you is completely in your hands.

We've designed will to be the friendliest, easiest-to-teach bot anywhere, where even non-coders can hop in and add new functionality in a matter of minutes.  We hope you'll find him as friendly as we do!

---

## Hello, world

Let's start as simple as they come - a plugin for will to say hello.  Since he already comes with "hello", and "hi", in this example, we'll go with "bonjour!"

#### Step 1: Create a bonjour.py

This file can be called anything, but given the functionality, bonjour seems like a fair name.  Create the file in your plugins folder:

![Plugins folder with bonjour.py](/img/plugins_bonjour.gif)

In the `bonjour.py` file, add this:

```python
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class BonjourPlugin(WillPlugin):

    @respond_to("bonjour")
    def say_bonjour_will(self, message):
        """bonjour: I know how to say bonjour! In French!"""
        self.reply(message, "bonjour!")


```

Now, restart your will to load the new plugin, and you should be able to do this:

![Plugins folder with bonjour.py](/img/bonjour_chat.gif)

Easy, right?  Well, now that your mind is swimming with ideas, it's a good time to go through the ways will knows how to notice, and how he knows to respond.


## What will can notice

All of the ways will can notice actions are specified using decorators - we'll give an example of each below.


#### Respond to direct mentions

Simple enough - if you directly @will mention him in a message, he'll see these.  It's exactly what we used in the example above.

```
@respond_to("bonjour")
def say_bonjour_will(self, message):
    # Awesome stuff
```

`@respond_to` takes a number of options:

```
@respond_to(regex, include_me=False, case_sensitive=False, multiline=False, admin_only=False)
```

- **regex**: a regular expression to match.
- **include_me**: whether will should include the things he says as possible matches
- **case_sensitive**: should the regex be case sensitive?
- **multiline**: should the regex allow multiline matches?
- **admin_only**: only runs the command if the sender is specified as an administrator.

&nbsp; 

#### Hear in any message

Sometimes, you want will to take actions when he sees things in everyday conversation, even if it wasn't directly addressed to him.  That's what `@hear()` is for.

```
@hear("(?:ran into )?a bug")
def log_all_bugs(self, message):
    # Awesome stuff
```

`@hear` takes a the same options as `respond_to`:

```
@hear(regex, include_me=False, case_sensitive=False, multiline=False, admin_only=False)
```

- **regex**: a regular expression to match.
- **include_me**: whether will should include the things he says as possible matches
- **case_sensitive**: should the regex be case sensitive?
- **multiline**: should the regex allow multiline matches?
- **admin_only**: only runs the command if the sender is specified as an administrator.

&nbsp; 

#### Take an action on a schedule

It's one of the best things about robots - they never, ever forget.  Will's no exception.  The `@schedule` decorator makes scheduled tasks simple.

```python
@periodic(hour='10', minute='0', day_of_week="mon-fri")
def standup(self):
    self.say("@all Standup! %s" % settings.WILL_HANGOUT_URL)
```

Under the hood, `@periodic` uses [apscheduler](http://apscheduler.readthedocs.org/en/latest/cronschedule.html#available-fields) to provide its options, so you can use any of the following as keyword arguments:

- **year**: 4-digit year number
- **month**: month number (1-12)
- **day**: day of the month (1-31)
- **week**: ISO week number (1-53)
- **day_of_week**: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
- **hour**: hour (0-23)
- **minute**: minute (0-59)
- **second**: second (0-59)


For each of those keys, any of the following expressions are valid values:

- ***** (any): Fire on every value
- ***/a** (any): Fire every a values, starting from the minimum
- **a-b** (any): Fire on any value within the a-b range (a must be smaller than b)
- **a-b/c** (any): Fire every c values within the a-b range
- **xth y** (day): Fire on the x -th occurrence of weekday y within the month
- **last x** (day): Fire on the last occurrence of weekday x within the month
- **last** (day): Fire on the last day within the month
- **x,y,z** (any): Fire on any matching expression; can combine any number of any of the above expressions


Awesome, right?


#### Handle webhooks and web pages

That's right. Will's also a full-fledged webserver under the hood, thanks to [bottle](http://bottlepy.org).  Using `@route`, he can handle webhooks, talk to chat, and render full HTML pages.

```python
# Simple
@route("/ping")
def ping(self):
    return "PONG"

# Render a template with jinja
@route("/keep-alive")
@rendered_template("keep_alive.html")
def keep_alive(self):
    return {}

# With full control, multiple templates, still connected to chat.
@route("/complex_page/<page_id:int>", method=POST)
def complex_page(self, page_id):
    # Talk to chat
    self.say("Hey, somebody's loading the complex page.")
    # Get JSON post data:
    post_data = self.request.json

    # Render templates
    header = rendered_template("header.html", post_data)
    some_other_context = {"page_id": page_id}
    some_other_context["header"] = header
    return rendered_template("complex_page.html", some_other_context)
```

#### Do things randomly

Variety is the spice of life, and nobody wants a robot without at least a *little* personality.  So, will's `@randomly` decorator allows you to specify actions that happend randomly, within a window.

```python
@randomly(start_hour='10', end_hour='17', day_of_week="mon-fri", num_times_per_day=1)
def walkmaster(self):
    self.say("@all time for a walk!")
```

`@randomly` accepts a few arguments:

```
@randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1):
```

- **start_hour**:  When to start the random window.
- **end_hour**:  When to end the random window.
- **day_of_week**:  What days of the week is the window available? Parsed with [apscheduler](http://apscheduler.readthedocs.org/en/latest/cronschedule.html#available-fields).
- **num_times_per_day**:  How many times per day within the window, should actions happen?


- How will can reply
    - Talk to the room
    - Reply to a person
    - Say something in the future
    - Talk to the room from a webhook
    - Send an email
    - Do any python thing
        - API endpoint
        - etc
    - PRs welcome (sms, etc)

- Creating a plugin
    - File, Class, inhertiance
    - Documentation
    - decorators
    - stacking

- Organize your plugins
    - Modules
    
    - Help text
    - Config of external libs

- Use the included batteries
    - Template rendering
    - Storage
        self.save()
        self.load()
    - Settings and require_settings
    - Natural time parsing
    - self.Rooms
    - self.users
    - Decorators are chainable

- Use the included plugins
    - Admin
        - Keepalive
        - Ping
        - Say
        - Storage
    - Chat rooms
        - rooms
        - roster
        - set_topic
    - Devops
        - emergency contacts
        - github status
        - heroku status
    - Friendly
        - Cookies
        - Hello
        - Love
        - Mornin'
        - Thanks
    - Help
        - Help
        - Programmer help
    - Productivity
        - Hangout
        - Image me
        - Remind me
        - World time
    - Web
        - Home

- Configure will
    - Which rooms to join
    - Admins
    - Default room
    - Environment and config.py
    - python run_will is helpful