from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template


class HomePagePlugin(WillPlugin):

    @route("/")
    @rendered_template("home.html")
    def homepage_listener(self):
        return {}
