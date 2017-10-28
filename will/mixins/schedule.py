import datetime
import logging
import random
import time
import traceback
from apscheduler.triggers.cron import CronTrigger
from will.mixins.pubsub import PubSubMixin


class ScheduleMixin(PubSubMixin, object):

    def times_key(self, periodic_list=False):
        if periodic_list:
            return "will_periodic_times_list"
        return "will_schedule_times_list"

    def schedule_key(self, periodic_list=False):
        if periodic_list:
            return "will_periodic_list"
        return "will_schedule_list"

    def get_schedule_list(self, periodic_list=False):
        return self.load(self.schedule_key(periodic_list=periodic_list), {})

    def save_schedule_list(self, new_list, periodic_list=False):
        self.save(self.schedule_key(periodic_list=periodic_list), new_list)

    def get_times_list(self, periodic_list=False):
        return self.load(self.times_key(periodic_list=periodic_list), {})

    def save_times_list(self, new_list, periodic_list=False):
        return self.save(self.times_key(periodic_list=periodic_list), new_list)

    # TODO: Create new version of this that's properly abstracted, instead of get_user_from_message
    def add_direct_message_to_schedule(self, when, content, message, target_user, *args, **kwargs):
        # target_user = self.get_user_from_message(message)
        self.add_to_schedule(when, {
            "type": "direct_message",
            "content": content,
            "target_jid": target_user["jid"],
            "args": args,
            "kwargs": kwargs,
        })

    def add_room_message_to_schedule(self, when, content, room, *args, **kwargs):
        self.add_to_schedule(when, {
            "type": "room_message",
            "content": content,
            "room": room,
            "args": args,
            "kwargs": kwargs,
        })

    def add_outgoing_event_to_schedule(self, when, event, *args, **kwargs):
        self.add_to_schedule(when, event, *args, **kwargs)

    def add_to_schedule(self, when, item, periodic_list=False, ignore_scheduler_lock=False):
        try:
            while (
                (ignore_scheduler_lock is False and self.load("scheduler_lock", False)) or
                self.load("scheduler_add_lock", False)
            ):
                import sys
                sys.stdout.write("waiting for lock to clear\n")
                time.sleep(random.random())

            self.save("scheduler_add_lock", True)
            sched_list = self.get_schedule_list(periodic_list=periodic_list)
            times_list = self.get_times_list(periodic_list=periodic_list)
            item["when"] = when
            item_hash = hash(repr(sorted(item.items())))
            item["hash"] = item_hash
            sched_list[item_hash] = item
            times_list[item_hash] = when
            self.save_schedule_list(sched_list, periodic_list=periodic_list)
            self.save_times_list(times_list, periodic_list=periodic_list)

        except:
            logging.critical(
                "Error adding to schedule at %s.  \n\n%s\nContinuing...\n",
                when,
                traceback.format_exc()
            )
        self.save("scheduler_add_lock", False)

    def remove_from_schedule(self, item_hash, periodic_list=False):
        # If this is ever called from anywhere outside the scheduler_lock, it needs its own lock.
        sched_list = self.get_schedule_list(periodic_list=periodic_list)
        times_list = self.get_times_list(periodic_list=periodic_list)
        del sched_list[item_hash]
        del times_list[item_hash]
        self.save_schedule_list(sched_list, periodic_list=periodic_list)
        self.save_times_list(times_list, periodic_list=periodic_list)

    def add_periodic_task(self, module_name, cls_name, function_name, sched_args,
                          sched_kwargs, ignore_scheduler_lock=False):
        now = datetime.datetime.now()
        ct = CronTrigger(*sched_args, **sched_kwargs)
        when = ct.get_next_fire_time(now)
        logging.info("ct.get_next_fire_time(now)")
        logging.info(when)
        item = {
            "type": "periodic_task",
            "module_name": module_name,
            "class_name": cls_name,
            "function_name": function_name,
            "sched_args": sched_args,
            "sched_kwargs": sched_kwargs,
        }
        self.add_to_schedule(when, item, periodic_list=True, ignore_scheduler_lock=ignore_scheduler_lock)

    def add_single_random_task(self, when, module_name, cls_name, function_name, start_hour, end_hour,
                               day_of_week, num_times_per_day, ignore_scheduler_lock=False):
        item = {
            "type": "random_task",
            "module_name": module_name,
            "class_name": cls_name,
            "function_name": function_name,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "day_of_week": day_of_week,
            "num_times_per_day": num_times_per_day,
        }

        self.add_to_schedule(when, item, periodic_list=True, ignore_scheduler_lock=ignore_scheduler_lock)

    def add_random_tasks(self, module_name, cls_name, function_name, start_hour, end_hour, day_of_week,
                         num_times_per_day, ignore_scheduler_lock=False):
        # This function is fired at startup, and every day at midnight.
        if end_hour < start_hour:
            raise Exception("start_hour is after end_hour!")

        # Get the next appropriate date
        now = datetime.datetime.now()

        # Work around crontab bug where if the hour has started, it's skipped.
        adjusted_start_hour = start_hour
        if adjusted_start_hour != 23:
            adjusted_start_hour += 1
        adjusted_start_hour = "%s" % adjusted_start_hour

        ct = CronTrigger(hour=adjusted_start_hour, day_of_week=day_of_week)
        fire_time = ct.get_next_fire_time(now)

        # If it's today, schedule it. Otherwise, it'll be scheduled at midnight of its run day.
        if fire_time.day == now.day:

            # There are more efficient ways to do this, but this supports almost any n for num_times_per_day,
            # and that seems more useful.
            possible_times = []
            for i in range(start_hour, end_hour):
                for j in range(60):
                    possible_times.append((i, j))

            times = random.sample(possible_times, num_times_per_day)
            for hour, minute in times:
                when = datetime.datetime(now.year, now.month, now.day, hour, minute)

                # If we're starting up mid-day, this may not be true.
                if when >= now:
                    self.add_single_random_task(
                        when, module_name, cls_name, function_name,
                        start_hour, end_hour, day_of_week, num_times_per_day,
                        ignore_scheduler_lock=ignore_scheduler_lock
                    )
