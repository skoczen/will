<img  align="right" src="https://gk-will.s3.amazonaws.com/will-head.png?v2" alt="Will's smilling face" title="Will's smilling face"/>

Meet Will.

Will is the friendliest, easiest-to-teach bot you've ever used.  He works on hipchat, in rooms and 1-1 chats.  Batteries included.

Quick-links:
- [Examples](README.md#will-can)
- [High-level API:](README.md#high-level-api)
    - [Plugin method decorators](README.md#plugin-method-decorators)
    - [High-level helpers](README.md#high-level-helpers)
    - [Advanced Topics](README.md#advanced-topics)
- [Installation:](README.md#installation)
    - [Starting a new Will](README.md#starting-a-new-will)
    - [Deploying on Heroku](README.md#deploying-on-heroku)
    - [Hacking on Will](README.md#hacking-on-will)
- [The Shoulders of Giants](README.md#the-shoulders-of-giants)
- [Releases](README.md#releases)

# Will can:

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

@respond_to("^hi")   # Basic
def hi(self, message):
    self.reply(message, "hello, %s!" % message.sender.nick)

@respond_to("award (?P<num_stars>\d)+ gold stars? to (?P<user_name>.*)")   # With named matches
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


#### Talk in HTML and plain text

roster.py

```python
@respond_to("who do you know about\?")
def list_roster(self, message):
    context = {"internal_roster": self.internal_roster.values(),}
    self.say(rendered_template("roster.html", context), message=message, html=True)
```

roster.html
```html
Here's who I know: <br>
<ul>
    {% for user in internal_roster %}
    <li><b>@{{user.nick|lower}}</b> - {{user.name}}.  (# {{user.hipchat_id}})</li>
    {% endfor %}
</ul>
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
```

Then:
> <b>You:</b> @will remind me to take out the trash at 6pm tomorrow<br>
> <b>Will:</b> take out the trash tomorrow at 6pm. Got it.

or:
> <b>You:</b> @will remind me to take out the trash at 6pm monday<br>
> <b>Will:</b> take out the trash December 16 at 6pm. Got it.


#### Document himself
```python
@respond_to("image me (?P<search_query>.*)$")
def image_me(self, message, search_query):
    """image me ___ : Search google images for ___, and post a random one."""
    pass
```

Then:
> <b>You:</b> @will help<br>
> <b>Will:</b> Sure thing, Steven. <br>
> <b>Will:</b> Here's what I know how to do:<br><b>&nbsp; &nbsp;image me ___</b> : Search google images for ___, and post a random one.


#### A lot more
We've built will to be easy to extend, change, and write.  Check out the plugins directory for lots more examples!

You can also take a look at [our will](https://github.com/greenkahuna/our-will).  He's open-source, handles our deploys and lots of fun things - enjoy!

3. Run `./start_dev_will.py` to start up just core will.
