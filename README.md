Will
====

Will is a simple python bot that's beautiful to use.

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
    export WILL_USERNAME='12345_123456@chat.hipchat.com'
    export WILL_PASSWORD='asj2498q89dsf89a8df'
    export WILL_TOKEN='kjadfj89a34878adf78789a4fae3'
    export WILL_V2_TOKEN='asdfjl234jklajfa3azfasj3afa3jlkjiau'
    export WILL_ROOMS='Testing, Will Kahuna;GreenKahuna'  # Semicolon-separated, so you can have commas in names.
    export WILL_NAME='William T. Kahuna'
    export WILL_HANDLE='will'
    export WILL_REDIS_URL="redis://localhost:6379/7"
    export WILL_HTTPSERVER_PORT="80"

    # Optional
    export WILL_DEFAULT_ROOM='12345_room1@conf.hipchat.com'
    ```
3. Run will. `will`


## Sample Code:

Will was designed to make building a bot easy, fun, and simple.  Here are some examples.

```python
import datetime
from gkbot import BotPlugin, respond_to, scheduled, one_time_task, hear, randomly, crontab
from gkbot import settings

class GoldStarPlugin(BotPlugin):

    @respond_to("award (?P<num_stars>\d)+ gold stars? to (?P<user_name>.*)")
    def gold_stars(self, message, num_stars=1, user_name=None):
        stars = self.load("gold_stars", {})
        if user_name in stars:
            stars[user_name] += num_stars
        else:
            stars[user_name] = num_stars

        self.save("gold_stars", stars)

        self.say("Awarded %s stars to %s." % (num_stars, user_name) )


class RemindMePlugin(BotPlugin):

    @respond_to("remind me to (?P<action>\w)+ at (?P<time>.*)")
    def remind_me(self, message, action, time):
        # Generate time_string ("at 5pm, tomorrow at 2pm, Dec 5 at 12")
        time_string = "at 5pm"
        self.say("You got it. I'll remind you %s" % time_string)

        @one_time_task(when=datetime.datetime.now())
        def remind_me(self):
            self.say("@%s, you asked me to remind you to %s.", html=False)


class StandupPlugin(BotPlugin):

    @scheduled(run_every=crontab(hour=10, minute=0))
    def standup(self):
        self.say("@all Standup! %s" % settings.STANDUP_URL)


class CookiesPlugin(BotPlugin):

    @hear("cookies", include_me=False)
    def will_likes_cookies(self):
        self.say(rendered_template("cookies.html", {}))


class WalkmasterPlugin(BotPlugin):

    @randomly(start_hour=8, end_hour=6, weekdays_only=True)
    def go_for_a_walk(self):
        self.say("@all time for a walk!")
        self.set_topic("Walk Time!")


class KeepAlivePlugin(BotPlugin):

    @scheduled(run_every=crontab(minute=1))
    def go_for_a_walk(self):
        requests.get("%s/keep-alive" % settings.WILL_URL)

    @route("/keep-alive")
    def keep_alive(self):
        return rendered_template("keep_alive.html", {})
```
