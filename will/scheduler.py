import logging
import datetime
import imp
import time
import traceback
import threading

from will.mixins import ScheduleMixin, PluginModulesLibraryMixin


class Scheduler(ScheduleMixin, PluginModulesLibraryMixin):

    @classmethod
    def clear_locks(cls, bot):
        bot.save("scheduler_add_lock", False)
        bot.save("scheduler_lock", False)
        bot.save("will_periodic_list", {})
        bot.save("will_periodic_times_list", {})

    def start_loop(self, bot):
        self.bot = bot
        # For other mixins that expect save.
        self.save = self.bot.save
        self.load = self.bot.load

        self.active_processes = []

        try:
            while True:
                self.check_scheduled_actions()
                time.sleep(0.9)
        except (KeyboardInterrupt, SystemExit):
            pass

    def _clear_random_tasks(self):
        self.bot.save("scheduler_lock", True)
        periodic_list = self.bot.get_schedule_list(periodic_list=True)
        periodic_times_list = self.bot.get_times_list(periodic_list=True)

        new_periodic_list = {}
        new_periodic_times_list = {}

        for item_hash, item in periodic_list.items():
            if not "random_task" in item:
                new_periodic_list[item_hash] = item
                new_periodic_times_list[item_hash] = periodic_times_list[item_hash]

        self.bot.save_schedule_list(new_periodic_list, periodic_list=True)
        self.bot.save_times_list(new_periodic_times_list, periodic_list=True)

        self.bot.save("scheduler_lock", False)

    def _run_applicable_actions_in_list(self, now, periodic_list=False):
        times_list = self.bot.get_times_list(periodic_list=periodic_list)

        # Iterate through times_list first, before loading the full schedule_list into memory (big pickled stuff, etc)
        a_task_needs_run = False
        for task_time in times_list.values():
            if task_time < now:
                a_task_needs_run = True
                break

        if a_task_needs_run:
            sched_list = self.bot.get_schedule_list(periodic_list=periodic_list)
            for item in sched_list.values():
                running_task = False
                try:

                    if item["when"] < now:
                        running_task = True
                        self.run_action(item)
                except:
                    logging.critical(
                        "Error running task %s.  \n\n%s\n"
                        "Trying to delete it and recover...\n",
                        item,
                        traceback.format_exc()
                    )

                if running_task:
                    try:
                        self.bot.remove_from_schedule(item["hash"], periodic_list=periodic_list)
                    except:
                        logging.critical(
                            "Unable to remove task. Leaving it in, you'll have to clean it out by hand."
                            "Sorry! \n\n%s\nContinuing...\n" % (traceback.format_exc(),)
                        )

    def check_scheduled_actions(self):
        now = datetime.datetime.now()

        # Re-schedule random tasks at midnight
        if not hasattr(self, "last_random_schedule"):
            self.last_random_schedule = self.bot.load("last_random_schedule")

        if self.last_random_schedule is None or self.last_random_schedule.day != now.day:
            self.bot.save("last_random_schedule", now)
            self.last_random_schedule = now
            self._clear_random_tasks()
            for plugin_info, fn, function_name in self.bot.random_tasks:
                meta = fn.will_fn_metadata
                self.add_random_tasks(
                    plugin_info["full_module_name"],
                    plugin_info["name"],
                    function_name,
                    meta["start_hour"],
                    meta["end_hour"],
                    meta["day_of_week"],
                    meta["num_times_per_day"]
                )
        try:
            if not self.bot.load("scheduler_add_lock", False) or not self.bot.load("scheduler_lock", False):
                self.bot.save("scheduler_lock", True)
                self._run_applicable_actions_in_list(now,)
                self._run_applicable_actions_in_list(now, periodic_list=True)
                self.bot.save("scheduler_lock", False)
        except:
            logging.critical("Scheduler run blew up.\n\n%s\nContinuing...\n", traceback.format_exc())

    def run_action(self, task):

        if task["type"] == "message" and "topic" in task:
            self.publish(task["topic"], task["event"])
            # self.bot.send_room_message(task["room"]["room_id"], task["content"], *task["args"], **task["kwargs"])
        elif task["type"] == "direct_message":
            user = self.bot.get_user_by_jid(task["target_jid"])
            self.bot.send_direct_message(user["hipchat_id"], task["content"], *task["args"], **task["kwargs"])
        elif task["type"] == "periodic_task":
            # Run the task
            module_info = self.plugin_modules_library[task["module_name"]]
            module = imp.load_source(module_info["name"], module_info["file_path"])
            cls = getattr(module, task["class_name"])
            fn = getattr(cls(), task["function_name"])

            thread = threading.Thread(target=fn)
            thread.start()

            # Schedule the next one.
            self.bot.add_periodic_task(
                task["module_name"],
                task["class_name"],
                task["function_name"],
                task["sched_args"],
                task["sched_kwargs"],
                ignore_scheduler_lock=True
            )
        elif task["type"] == "random_task":
            # Run the task
            module_info = self.plugin_modules_library[task["module_name"]]
            module = imp.load_source(module_info["name"], module_info["file_path"])
            cls = getattr(module, task["class_name"])
            fn = getattr(cls(), task["function_name"])

            thread = threading.Thread(target=fn)
            thread.start()

            # The next one will be auto-scheduled at midnight
