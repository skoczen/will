Will
====

Will is a simple python bot that's beautiful to use.

Will is the friendliest, easiest-to-teach bot you've ever used.

## He can:

### Hear

```python
class CookiesPlugin(WillPlugin):
    @hear("cookies", include_me=False)
    def will_likes_cookies(self, message):
        self.say("I LOOOOVE COOOKIEEESS!!!")
```

### Reply

### Do things on a schedule.

### Do things randomly

### Respond to webhooks
@rendered_template("keep_alive.html")
and 
rendered_template("keep_alive.html", {})

### Talk in HTML and plain text


## Full API:

### Plugin decorators
```
@hear(regex, include_me=False, case_sensitive=False)
@respond_to(regex, include_me=False, case_sensitive=False)
@periodic()
@randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1)
@route(bottle_route)

@rendered_template("template_name.html")
```

### High-level chat methods
```
self.say(content, message=None, room=None, html=False, color="green", notify=False)
self.reply(message, content, html=False, color="green", notify=False)
    # note html is stripped for 1-1 messages
self.set_topic(self, topic, message=None, room=None)
    # note you can't set the topic of a 1-1
self.schedule_say(content, when, message=None, room=None, html=False, color="green", notify=False)
```

### High-level helpers:

```
self.rendered_template(template_name, context={})
```


### Low-level chat methods:


Advanced
- change topic
- multiple rooms
- 1-1 chat



Will supports:
- Replies
- Scheduled tasks
- One-time tasks
- Random tasks
- Every-message listening
- A web server, via Bottle
- Full HTML templating, via Jinja


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
