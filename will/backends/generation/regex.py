import requests

from will import settings
from will.decorators import require_settings
from .base import GenerateBackend

class RegexBackend(GenerateBackend):

    def generate(self, message, context):
        return {}