import requests

from will import settings
from will.decorators import require_settings
from .base import ExecutionBackend

class AllBackend(object):

    def execute(self, message, context):
        return {}
