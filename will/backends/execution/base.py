from will import settings
from will.decorators import require_settings


class ExecutionBackend(object):
    is_will_execution_backend = True

    def execute(self, message, context):
        raise NotImplemented
