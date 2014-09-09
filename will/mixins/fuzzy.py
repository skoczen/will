from will import settings

class FuzzyMixin(object):
    @property
    def get_max_num_regexes(self, q=None):
        return min(max(len(l['regex']) for l in self.message_listeners), settings.MAX_ALLOWED_TYPOS) 

