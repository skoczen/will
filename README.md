Will
====

Will is the friendliest, easiest-to-teach bot you've ever used.  He works on hipchat, in rooms and 1-1 chats.

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
    self.say("@all time for a walk!")
```

#### Schedule things on the fly
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
    # Talk to chat
    self.say("Hey, somebody's loading the complex page.")
    # Render templates
    header = rendered_template("header.html")
    some_other_context = {}
    some_other_context["header"] = header
    return rendered_template("complex_page.html", some_other_context)
```


#### Talk in HTML and plain text

```python
@respond_to("who do you know about\?")
def list_roster(self, message):
    context = {"internal_roster": self.internal_roster.values(),}
    self.say(rendered_template("roster.html", context), message=message, html=True)
```

roster.html
```html
Here's who I know: <br>
{% for user in internal_roster %}
- <b>@{{user.nick|lower}}</b> - {{user.name}}.  (#{{user.hipchat_id}})</li>
{% endfor %}
```

#### Understand natural time
```python
@respond_to("remind me to (?P<reminder_text>.*?) (at|on) (?P<remind_time>.*)")
def remind_me_at(self, message, reminder_text=None, remind_time=None):
    
    # Parse the time
    now = datetime.datetime.now()
    parsed_time = self.parse_natural_time(remind_time)

    # Make a friendly reply
    natural_datetime = self.to_natural_day_and_time(parsed_time)

    # Schedule the reminder    
    formatted_reminder_text = "@%(from_handle)s, you asked me to remind you %(reminder_text)s" % {
        "from_handle": message.sender.nick,
        "reminder_text": reminder_text,
    }
    self.schedule_say(formatted_reminder_text, parsed_time, message=message)

    # Confirm that he heard you.
    self.say("%(reminder_text)s %(natural_datetime)s. Got it." % locals(), message=message)

# e.g.
# @will remind me to take out the trash at 6pm tomorrow
# > take out the trash tomorrow at 6pm. Got it.
# or
# @will remind me to take out the trash at 6pm monday
# > take out the trash December 16 at 6pm. Got it.
```


## Full API:

### Plugin decorators

`@hear(regex, include_me=False, case_sensitive=False)`

    - `regex`: a regular expression to match.
    - `include_me`: whether will should hear what he says
    - `case_sensitive`: should the regex be case sensitive?

`@respond_to(regex, include_me=False, case_sensitive=False)`

    - `regex`: a regular expression to match.
    - `include_me`: whether will should hear what he says
    - `case_sensitive`: should the regex be case sensitive?

`@periodic(*periodic_args)`

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

`@randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1)`

    - `start_hour`: the earliest a random task could fall.
    - `end_hour`: the latest hour a random task could fall (inclusive, so end_hour:59 is a possible time.)
    - `day_of_week`: valid days of the week, same expressions available as `@periodic`
    - `num_times_per_day`: number of times this task should happen per day.

`@route(routing_rule)`

    - `routing_rule`:  A [bottle routing rule](http://bottlepy.org/docs/dev/routing.html). 

`@rendered_template("template_name.html")`

    - `"template_name.html"`: the path to the template, relative to the `templates` directory. Assumes the function returns a dictionary, to be used as the template context.


### High-level chat methods
```python
self.say(content, message=None, room=None, html=False, color="green", notify=False)
self.reply(message, content, html=False, color="green", notify=False)
    # note html is stripped for 1-1 messages
self.set_topic(self, topic, message=None, room=None)
    # note you can't set the topic of a 1-1 chat
self.schedule_say(content, when, message=None, room=None, html=False, color="green", notify=False)
```

#### High-level helpers
```python
self.parse_natural_time(remind_time)
self.to_natural_day_and_time(parsed_time)
self.rendered_template(template_name, context={})
```


Advanced:
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



### Deploying on heroku
- forking
- pip installing


### Shoulders of Giants

Will leverages some fantastic libraries.  He wouldn't exist without them.

- [Bottle](http://bottlepy.org/docs/dev/) for http handling
- [Jinja](http://jinja.pocoo.org/) for templating
- [Sleekxmpp](http://sleekxmpp.com/) for listening to xmpp
- [natural](https://github.com/tehmaze/natural) and [parsedatetime](https://github.com/bear/parsedatetime) for natural date parsing
- [apscheduler](http://apscheduler.readthedocs.org/en/latest/) for scheduled task parsing
- [Requests](http://requests.readthedocs.org/en/latest/) to make http sane.
