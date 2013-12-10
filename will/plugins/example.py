import datetime
import requests
from will.plugin_base import WillPlugin
from will.decorators import respond_to, periodic, one_time_task, hear, randomly, route, rendered_template
import will.settings as settings

def crontab(*args, **kwargs):
    # Stub
    pass


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

    # @periodic(run_every=crontab(minute=1))
    # def go_for_a_walk(self):
    #     requests.get("%s/keep-alive" % settings.WILL_URL)

    @route("/keep-alive")
    def keep_alive(self):
        return rendered_template("keep_alive.html", {})


