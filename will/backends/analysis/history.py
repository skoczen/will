import requests

from will import settings
from will.mixins import StorageMixin
from will.decorators import require_settings
from .base import AnalysisBackend


class HistoryAnalysis(AnalysisBackend, StorageMixin):

    def do_analyze(self, message):
        # Load the last few messages, add it to the context under "history"
        history = self.load("message_history", [])
        if not history:
            history = []
        max_history_context = getattr(settings, "HISTORY_CONTEXT_LENGTH", 20)

        if history:
            context = {
                "history": history[:max_history_context]
            }
        else:
            context = {
                "history": [],
            }

        history.append(message)
        self.save("message_history", history)

        return context
