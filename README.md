Will
====

Will is the friendliest, easiest-to-teach bot you've ever used.

### He can:

#### Hear

```python
class CookiesPlugin(WillPlugin):

    @hear("cookies")
    def will_likes_cookies(self, message):
        self.say("I LOOOOVE COOOKIEEESS!!!")
```

#### Reply
```python
# All examples below are impled to be on a subclass of WillPlugin

# Basic
@respond_to("^hi")
def hi(self, message):
    self.reply(message, "hello, %s!" % message.sender.nick)

# With named matches
@respond_to("award (?P<num_stars>\d)+ gold stars? to (?P<user_name>.*)")
def gold_stars(self, message, num_stars=1, user_name=None):
    stars = self.load("gold_stars", {})
    stars[user_name] += num_stars
    self.save("gold_stars", stars)

    self.say("Awarded %s stars to %s." % (num_stars, user_name), message=message)
```

#### Do things on a schedule.

```python
@periodic(hour='10', minute='0', day_of_week="mon-fri")
def standup(self):
    self.say("@all Standup! %s" % settings.WILL_HANGOUT_URL)
```

#### Do things randomly
```python
@randomly(start_hour='10', end_hour='17', day_of_week="mon-fri", num_times_per_day=1)
def walkmaster(self):
    now = datetime.datetime.now()
    in_5_minutes = now + datetime.timedelta(minutes=5)

    self.say("@all Walk happening in 5 minutes!")
    self.schedule_say("@all It's walk time!", in_5_minutes)
```

#### Remember

Will can remember [almost any](https://pypi.python.org/pypi/dill) python object, even across reboots.

```python
self.save("my_key", "my_value")
self.load("my_key", "default value")
```

#### Respond to webhooks

```python
# Simply
@route("/ping")
def ping(self):
    return "PONG"

# With templates
@route("/keep-alive")
@rendered_template("keep_alive.html")
def keep_alive(self):
    return {}

# With full control, multiple templates, still connected to chat.
@route("/complex_page/")
def complex_page(self):
    
    self.say("Hey, somebody's loading the complex page.")

    header = rendered_template("header.html")
    some_other_context = {}
    some_other_context["header"] = header
    return rendered_template("complex_page.html", some_other_context)
```


#### Talk in HTML and plain text

```python
@respond_to("who do you know about?")
def list_roster(self, message):
    context = {"internal_roster": self.internal_roster.values(),}
    self.say(rendered_template("roster.html", context), message=message, html=True)
```

#### Understand natural time
```python
@respond_to("remind me to (?P<reminder_text>.*?) (at|on) (?P<remind_time>.*)")
def remind_me_at(self, message, reminder_text=None, remind_time=None):
    now = datetime.datetime.now()
    parsed_time = self.parse_natural_time(remind_time)
    natural_datetime = self.to_natural_day_and_time(parsed_time)
    self.say("%(reminder_text)s %(natural_datetime)s. Got it." % locals(), message=message)
```


## Full API:

### Plugin decorators
```
<dl>
    <dt>``@hear(regex, include_me=False, case_sensitive=False)``</dt>
    <dd>
        - `regex`: a regular expression to match.
        - `include_me`: whether will should hear what he says
        - `case_sensitive`: should the regex be case sensitive?
    </dd>
    
    <dt>`@respond_to(regex, include_me=False, case_sensitive=False)`</dt>
    <dd>
        - `regex`: a regular expression to match.
        - `include_me`: whether will should hear what he says
        - `case_sensitive`: should the regex be case sensitive?
    </dd>
    
    <dt>`@periodic(*periodic_args)<`/dt>
    <dd>
        Args are parsed by [apscheduler](http://apscheduler.readthedocs.org/en/latest/cronschedule.html#available-fields).

        - `year`: 4-digit year number
        - `month`: month number (1-12)
        - `day`: day of the month (1-31)
        - `week`: ISO week number (1-53)
        - `day_of_week`: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        - `hour`: hour (0-23)
        - `minute`: minute (0-59)
        - `second`: second (0-59)

        The following expressions are valid:

        - `*` (any): Fire on every value
        - `*/a` (any): Fire every a values, starting from the minimum
        - `a-b` (any): Fire on any value within the a-b range (a must be smaller than b)
        - `a-b/c` (any): Fire every c values within the a-b range
        - `xth y` (day): Fire on the x -th occurrence of weekday y within the month
        - `last x` (day): Fire on the last occurrence of weekday x within the month
        - `last` (day): Fire on the last day within the month
        - `x,y,z` (any): Fire on any matching expression; can combine any number of any of the above expressions
    </dd>
    
    <dt>`@randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1)<`/dt>
    <dd>
        - `start_hour`: the earliest a random task could fall.
        - `end_hour`: the latest hour a random task could fall (inclusive, so end_hour:59 is a possible time.)
        - `day_of_week`: valid days of the week, same expressions available as `@periodic`
        - `num_times_per_day`: number of times this task should happen per day.
    </dd>
    
    <dt>`@route(routing_rule)<`/dt>
    <dd>
        - `routing_rule`:  A [bottle routing rule](http://bottlepy.org/docs/dev/routing.html). 
    </dd>

    <dt>`@rendered_template("template_name.html")`</dt>
    <dd>
        - `"template_name.html"`: the path to the template, relative to the `templates` directory. Assumes the function returns a dictionary, to be used as the template context.
    </dd>
</dl>

```

### High-level chat methods
```
self.say(content, message=None, room=None, html=False, color="green", notify=False)
self.reply(message, content, html=False, color="green", notify=False)
    # note html is stripped for 1-1 messages
self.set_topic(self, topic, message=None, room=None)
    # note you can't set the topic of a 1-1
self.schedule_say(content, when, message=None, room=None, html=False, color="green", notify=False)
self.parse_natural_time(remind_time)
self.to_natural_day_and_time(parsed_time)
```

### High-level helpers:

```
self.rendered_template(template_name, context={})
```


### Low-level chat methods:


Advanced
- multiple rooms
- 1-1 chat


## Setup via pip
1. Install via `pip install will`, or fork and clone this repo.
2. Set environment variables:

   ```
    # Required
    export WILL_USERNAME='12345_123456@chat.hipchat.com'
    export WILL_PASSWORD='asj2498q89dsf89a8df'
    export WILL_TOKEN='kjadfj89a34878adf78789a4fae3'
    export WILL_V2_TOKEN='asdfjl234jklajfa3azfasj3afa3jlkjiau'
    export WILL_ROOMS='Testing, Will Kahuna;GreenKahuna'  # Semicolon-separated, so you can have commas in names.
    export WILL_NAME='William T. Kahuna'
    export WILL_HANDLE='will'
    export WILL_REDIS_URL="redis://localhost:6379/7"
   
   
    # Optional / Production

    # Default room: (otherwise defaults to the first of WILL_ROOMS)
    export WILL_DEFAULT_ROOM='12345_room1@conf.hipchat.com'  
    
    # For google hangouts:
    export WILL_HANGOUT_URL='https://plus.google.com/hangouts/_/event/ceggfjm3q3jn8ktan7k861hal9o'
    
    # If will isn't accessible at localhost (heroku, etc):
    export WILL_URL="http://my-will.herokuapp.com/"

    # Defaults to 80
    export WILL_HTTPSERVER_PORT="80"
    
    ```
3. Run will. `will`


## Sample Code:

Will was designed to make building a bot easy, fun, and simple.  Here are some examples.

To Doc:
- only need message if
    : reply
    : more than one room.


```python

class GoldStarPlugin(WillPlugin):

    @respond_to("award (?P<num_stars>\d)+ gold stars? to (?P<user_name>.*)")
    def gold_stars(self, message, num_stars=1, user_name=None):
        stars = self.load("gold_stars", {})
        if user_name in stars:
            stars[user_name] += num_stars
        else:
            stars[user_name] = num_stars

        self.save("gold_stars", stars)

        self.saymessage, ("Awarded %s stars to %s." % (num_stars, user_name))



class NewTopicPlugin(WillPlugin):

    @respond_to("new topic (?P<topic>.*)")
    def new_topic(self, message, topic="Something or other. You weren't terribly specific."):
        self.set_topic(message, topic)



class CookiesPlugin(WillPlugin):

    @hear("cookies", include_me=False)
    def will_likes_cookies(self, message):
        self.say(rendered_template("cookies.html", {}), message=message, html=True, )


class WalkmasterPlugin(WillPlugin):

    @randomly(start_hour=8, end_hour=6, weekdays_only=True)
    def go_for_a_walk(self):
        self.say("@all time for a walk!", room="GreenKahuna")
        self.set_topic("Walk Time!")


class KeepAlivePlugin(WillPlugin):

    @periodic(run_every=crontab(minute=1))
    def go_for_a_walk(self):
        requests.get("%s/keep-alive" % settings.WILL_URL)

    @route("/keep-alive")
    def keep_alive(self):
        return rendered_template("keep_alive.html", {})

```

### Deploying on heroku
- forking
- pip installing



### Shoulders of Giants

Will leverages some fantastic libraries.  He wouldn't exist without them.

* Bottle for http handling
* Jinja for templating
* Sleepxmpp for listening to xmpp
* natural and parsedatetime for natural date parsing
* apscheduler for scheduled task parsing
* Requests to make http sane.
