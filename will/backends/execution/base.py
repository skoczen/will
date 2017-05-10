from will import settings
from will.decorators import require_settings


class ExecutionBackend(object):
    is_will_execution_backend = True

    def execute(self, message, context):
        raise NotImplemented

    def __init__(self, bot=None, *args, **kwargs):
        self.bot = bot
        if not bot:
            raise Exception("Can't proceed without an instance of bot passed to the backend.")
        super(ExecutionBackend, self).__init__(*args, **kwargs)
