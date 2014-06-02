from bottle import route as bottle_route
from mixins import ScheduleMixin, StorageMixin


def respond_to(regex, include_me=False, case_sensitive=False, multiline=False):
    def wrap(f):
        passed_args = []

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.listener_regex = regex
        wrapped_f.case_sensitive = case_sensitive
        wrapped_f.multiline = multiline
        wrapped_f.listens_only_to_direct_mentions = True
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        wrapped_f.listener_args = passed_args
        wrapped_f.__doc__ = f.__doc__
        return wrapped_f

    return wrap


def periodic(*sched_args, **sched_kwargs):
    def wrap(f):

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.periodic_task = True
        wrapped_f.function_name = f.__name__
        wrapped_f.sched_args = sched_args
        wrapped_f.sched_kwargs = sched_kwargs
        return wrapped_f
    return wrap


def hear(regex, include_me=False, case_sensitive=False, multiline=False):
    def wrap(f):
        passed_args = []

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.listener_regex = regex
        wrapped_f.case_sensitive = case_sensitive
        wrapped_f.multiline = multiline
        wrapped_f.listens_only_to_direct_mentions = False
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        wrapped_f.listener_args = passed_args
        wrapped_f.__doc__ = f.__doc__
        return wrapped_f

    return wrap


def randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1):
    def wrap(f):

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.random_task = True
        wrapped_f.start_hour = int(start_hour)
        wrapped_f.end_hour = int(end_hour)
        wrapped_f.day_of_week = day_of_week
        wrapped_f.num_times_per_day = int(num_times_per_day)

        return wrapped_f
    return wrap


def rendered_template(template_name, context=None):
    import os
    from jinja2 import Environment, FileSystemLoader

    template_dirs = os.environ["WILL_TEMPLATE_DIRS_PICKLED"].split(";;")
    loader = FileSystemLoader(template_dirs)
    env = Environment(loader=loader)

    if context is not None:
        this_template = env.get_template(template_name)
        return this_template.render(**context)
    else:
        def wrap(f):
            def wrapped_f(*args, **kwargs):
                context = f(*args, **kwargs)
                if type(context) == type({}):
                    template = env.get_template(template_name)
                    return template.render(**context)
                else:
                    return context
            return wrapped_f
        return wrap


def route(path, *args, **kwargs):
    def wrap(f):
        f.bottle_route = path
        for k, v in kwargs.items():
            setattr(f, "bottle_%s" % k, v)
        return f
    return wrap
