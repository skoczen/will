import requests

from will import settings

class FuzzyMixin(object):
    @property
    def get_max_num_regexes(self, q=None):
        return min(max(len(listener.meta['regex']) for plugin in self.plugins), settings.MAX_ALLOWED_TYPOS) 

