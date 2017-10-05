import requests

from will import settings
from will.decorators import require_settings
from .base import AnalysisBackend


class NoAnalysis(AnalysisBackend):

    def do_analyze(self, message):
        return {}
