from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class SnickerdoodlesPlugin(WillPlugin):

    @hear("cookies", include_me=False)
    def will_likes_cookies(self, message):
        self.say(rendered_template("cookies.html", {}), message=message, html=True, )
