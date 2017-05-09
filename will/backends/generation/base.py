from will import settings
from will.decorators import require_settings


class GenerateBackend(object):

    def generate(self, message, context):
        raise NotImplemented
