from will import settings
from will.decorators import require_settings


class ExecutionBackend(object):

    def execute(self, message, context):
        raise NotImplemented
