from will import settings
from will.decorators import require_settings
from .base import GenerationBackend


class RegexBackend(GenerationBackend):

    def do_generate(self, message):
        return []
