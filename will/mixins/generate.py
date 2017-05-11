import requests

from will import settings
from will.decorators import require_settings


class GenerateMixin(object):

    def generate(self, message, context):
        return {}
