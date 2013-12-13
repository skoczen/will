import logging
import datetime
import time
import traceback
import threading

from mixins import ScheduleMixin, HipChatMixin, RosterMixin, StorageMixin
from plugin import WillPlugin

class Scheduler(ScheduleMixin):

    @classmethod
    def clear_locks(cls, bot):
        bot.save("scheduler_add_lock", False)
        bot.save("scheduler_lock", False)    
        bot.save("will_periodic_list", [])
        bot.save("will_periodic_times_list", [])

    def start_loop(self, bot):
        self.bot = bot
        self.active_processes = []

        try:
            while True:
                self.check_scheduled_actions()
                time.sleep(0.995)
        except (KeyboardInterrupt, SystemExit):
            pass

    def _clear_random_tasks(self):
        self.bot.save("scheduler_lock", True)
        periodic_list = self.bot.get_schedule_list(periodic_list=True)
        periodic_times_list = self.bot.get_times_list(periodic_list=True)
        
        new_periodic_list = []
        new_periodic_times_list = []
        
        for i in range(0, len(periodic_list)):
            task = periodic_list[i]
            if not "random_task" in task:
                new_periodic_list.append(task)
                new_periodic_times_list.append(periodic_times_list[i])
        
        self.bot.save_schedule_list(new_periodic_list, periodic_list=True)
        self.bot.save_times_list(new_periodic_times_list, periodic_list=True)
        
        self.bot.save("scheduler_lock", False)


    def _run_applicable_actions_in_list(self, now, periodic_list=False):
        times_list = self.bot.get_times_list(periodic_list=periodic_list)
        
        # Iterate through times_list first, before loading the full schedule_list into memory (big pickled stuff, etc)
        a_task_needs_run = False
        for task_time in times_list:
            if task_time < now:
                a_task_needs_run = True
                break

        if a_task_needs_run:
            sched_list = self.bot.get_schedule_list(periodic_list=periodic_list)
            for i in reversed(range(0, len(sched_list))):
                running_task = False
                try:

                    if sched_list[i]["when"] < now:
                        running_task = True
                        self.run_action(sched_list[i])
                except:
                    logging.critical("Error running task %s.  \n\n%s\nTrying to delete it and recover...\n" % (sched_list[i], traceback.format_exc() ))
                    
                if running_task:
                    try:
                        self.bot.remove_from_schedule(i, periodic_list=periodic_list)
                    except:
                        logging.critical("Unable to remove task. Leaving it in, you'll have to clean it out by hand. Sorry! \n\n%s\nContinuing...\n" % (traceback.format_exc(), ))


    def check_scheduled_actions(self):
        now = datetime.datetime.now()

        # Re-schedule random tasks at midnight
        if not hasattr(self, "last_random_schedule"):
            self.last_random_schedule = self.bot.load("last_random_schedule")

        if self.last_random_schedule is None or self.last_random_schedule.day != now.day:
            self.bot.save("last_random_schedule", now)
            self.last_random_schedule = now
            self._clear_random_tasks()
            for cls, fn in self.bot.random_tasks:
                self.bot.add_random_tasks(cls, fn, fn.start_hour, fn.end_hour, fn.day_of_week, fn.num_times_per_day)
        try:
            if not self.bot.load("scheduler_add_lock", False) or not self.bot.load("scheduler_lock", False):
                self.bot.save("scheduler_lock", True)
                self._run_applicable_actions_in_list(now,)
                self._run_applicable_actions_in_list(now, periodic_list=True)
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
            thread = threading.Thread(target=getattr(task["class"](),task["function"]))
            thread.start()

            # Schedule the next one.
            self.bot.add_periodic_task(task["class"], task["sched_args"], task["sched_kwargs"], task["function"], ignore_scheduler_lock=True)
        elif task["type"] == "random_task":
            # Run the task
            thread = threading.Thread(target=getattr(task["class"](),task["function"]))
            thread.start()

            # The next one will be auto-scheduled at midnight
