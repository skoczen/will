import datetime
from will import BotPlugin, respond_to, scheduled, one_time_task, hear, randomly, crontab, settings


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


