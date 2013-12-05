from bottle import route, run, template
from will.plugin_base import WillPlugin


@route("/test")
def test():
    return "Yo"