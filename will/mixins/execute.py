import requests

from will import settings
from will.decorators import require_settings


class ExecuteMixin(object):

    def execute(self, message, context):
        return {}
