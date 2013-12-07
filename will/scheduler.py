import logging
import datetime
import time
import traceback
from mixins import ScheduleMixin, HipChatAPIMixin, RosterMixin
from storage import StorageMixin

class Scheduler(ScheduleMixin, StorageMixin, HipChatAPIMixin, RosterMixin):

    def start_loop(self, bot):
        self.bot = bot
        self.save("scheduler_add_lock", False)
        self.save("scheduler_lock", False)
        try:
            while True: 
                self.check_scheduled_actions()
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass

    def check_scheduled_actions(self):
        if not self.load("scheduler_add_lock", False) or not self.load("scheduler_lock", False):
            now = datetime.datetime.now()
            self.save("scheduler_lock", True)
            sched_list = self.get_schedule_list()
            for i in reversed(range(0, len(sched_list))):
                try:
                    if sched_list[i]["when"] < now:
                        self.run_action(sched_list[i])
                        self.remove_from_schedule(i)
                except:
                    logging.critical("Error running task %s.  \n\n%s\nTrying to delete it and recover...\n" % (sched_list[i], traceback.format_exc() ))
                    try:
                        self.remove_from_schedule(i)
                    except:
                        logging.critical("Unable to remove task. Leaving it in, you'll have to clean it out by hand. Sorry! \n\n%s\nContinuing...\n" % (traceback.format_exc(), ))

                    
            self.save("scheduler_lock", False)

    def run_action(self, task):
        if task["type"] == "room_message":
            self.send_room_message(task["room"]["room_id"], task["content"], *task["args"], **task["kwargs"])
        elif task["type"] == "direct_message":
            user = self.get_user_by_jid(task["target_jid"])
            self.send_direct_message(user["hipchat_id"], task["content"], *task["args"], **task["kwargs"])
