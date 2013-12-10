import logging
import datetime
import time
import traceback

from mixins import ScheduleMixin, HipChatAPIMixin, RosterMixin
from storage import StorageMixin
from plugin_base import WillPlugin

class Scheduler(ScheduleMixin):

    def start_loop(self, bot):
        self.bot = bot

        try:
            while True: 
                self.check_scheduled_actions()
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass

    def _run_applicable_actions_in_list(self, sched_list, periodic_list=False):
        now = datetime.datetime.now()
        for i in reversed(range(0, len(sched_list))):
            try:
                if sched_list[i]["when"] < now:
                    self.run_action(sched_list[i])
                    self.bot.remove_from_schedule(i, periodic_list=periodic_list)
            except:
                logging.critical("Error running task %s.  \n\n%s\nTrying to delete it and recover...\n" % (sched_list[i], traceback.format_exc() ))
                try:
                    self.bot.remove_from_schedule(i, periodic_list=periodic_list)
                except:
                    logging.critical("Unable to remove task. Leaving it in, you'll have to clean it out by hand. Sorry! \n\n%s\nContinuing...\n" % (traceback.format_exc(), ))


    def check_scheduled_actions(self):
        try:
            if not self.bot.load("scheduler_add_lock", False) or not self.bot.load("scheduler_lock", False):
                self.bot.save("scheduler_lock", True)
                self._run_applicable_actions_in_list(self.bot.get_schedule_list())
                self._run_applicable_actions_in_list(self.bot.get_schedule_list(periodic_list=True), periodic_list=True)
                self.bot.save("scheduler_lock", False)
        except:
            logging.critical("Scheduler run blew up.\n\n%s\nContinuing...\n" % (traceback.format_exc(), ))

    def run_action(self, task):
        if task["type"] == "room_message":
            self.bot.send_room_message(task["room"]["room_id"], task["content"], *task["args"], **task["kwargs"])
        elif task["type"] == "direct_message":
            user = self.bot.get_user_by_jid(task["target_jid"])
            self.bot.send_direct_message(user["hipchat_id"], task["content"], *task["args"], **task["kwargs"])
        elif task["type"] == "periodic_task":
            # Run the task
            task["function"](task["class"]())

            # Schedule the next one.
            self.bot.add_periodic_task(task["class"], task["sched_args"], task["sched_kwargs"], task["function"], ignore_scheduler_lock=True)
