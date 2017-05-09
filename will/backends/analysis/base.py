from will import settings
from will.decorators import require_settings


class AnalysisBackend(object):

    def analyze(self, message, context):
        raise NotImplemented
