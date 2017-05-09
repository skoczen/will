import requests

from will import settings
from will.decorators import require_settings


class AnalyzeMixin(object):

    def analyze(self, message, context):
        # Call all ANALYZE_BACKENDS, return collected object with metadata.
        return {}