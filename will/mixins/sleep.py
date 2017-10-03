import random
import time
from will import settings


class SleepMixin(object):
    def sleep_for_event_loop(self):
        if not hasattr(self, "sleep_time"):
            self.sleep_time = settings.EVENT_LOOP_INTERVAL + (random.randint(0, 1) * settings.EVENT_LOOP_INTERVAL)

        time.sleep(self.sleep_time)
