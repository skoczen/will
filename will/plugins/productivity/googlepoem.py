from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
import requests
from xml.dom import minidom

class GooglePoemPlugin(WillPlugin):
    @respond_to("^gpoem (?P<topic>.*)$")
    def google_poem(self, message, topic):
        """gpoem __: show a google poem about __"""
        r = requests.get("http://www.google.com/complete/search?output=toolbar&q=" + topic + "%20")
        xmldoc = minidom.parseString(r.text)
        itemList = xmldoc.getElementsByTagName("suggestion")
        context = {"topic": topic, "lines": [x.attributes["data"].value for x in itemList[:4]] }
        self.say(rendered_template("gpoem.html", context), message, html=True)
