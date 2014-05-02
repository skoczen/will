from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class SnickerdoodlesPlugin(WillPlugin):

    @hear("snickerdoodles", include_me=False)
    def will_likes_snickerdoodles(self, message):
        """I am the cookie whisperer."""
        self.say(rendered_template("cookies.html", {}), message=message, html=True, )
