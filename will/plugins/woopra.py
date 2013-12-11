from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class WoopraPlugin(WillPlugin):

    @respond_to("^woopra me")
    def woopra_link(self, message):
        self.reply(message, "https://www.woopra.com/live/website/greenkahuna.com/dashboard")

    @route("/woopra/ie9")
    def ie9_visitor(self):
        json = self.request.json
        if not json:
            json = {"name": "Unknown name"}
        self.say("Hey team, we got an IE9 visitor (%(name)s). :(  <a href='https://www.woopra.com/live/website/greenkahuna.com/people'>Check out woopra for details</a>" % json, html=True)
        return ""