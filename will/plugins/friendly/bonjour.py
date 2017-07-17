# -- coding: utf-8 -
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class BonjourPlugin(WillPlugin):

    @respond_to("^bonjour$")
    def bonjour(self, message):
        """bonjour: Je parle un petit français aussi!"""
        self.reply(message, "bonjour!")
