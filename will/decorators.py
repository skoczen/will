def respond_to(regex, include_me=False, case_sensitive=False, multiline=False, admin_only=False):
    def wrap(f):
        passed_args = []

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})

        wrapped_f.will_fn_metadata["listener_regex"] = regex
        wrapped_f.will_fn_metadata["case_sensitive"] = case_sensitive
        wrapped_f.will_fn_metadata["multiline"] = multiline
        wrapped_f.will_fn_metadata["listens_only_to_direct_mentions"] = True
        wrapped_f.will_fn_metadata["listens_only_to_admin"] = admin_only
        wrapped_f.will_fn_metadata["listener_includes_me"] = include_me
        wrapped_f.will_fn_metadata["listens_to_messages"] = True
        wrapped_f.will_fn_metadata["listener_args"] = passed_args
        wrapped_f.will_fn_metadata["__doc__"] = f.__doc__
        return wrapped_f
    return wrap


def periodic(*sched_args, **sched_kwargs):
    def wrap(f):

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
        wrapped_f.will_fn_metadata["periodic_task"] = True
        wrapped_f.will_fn_metadata["function_name"] = f.__name__
        wrapped_f.will_fn_metadata["sched_args"] = sched_args
        wrapped_f.will_fn_metadata["sched_kwargs"] = sched_kwargs
        return wrapped_f
    return wrap


def hear(regex, include_me=False, case_sensitive=False, multiline=False, admin_only=False):
    def wrap(f):
        passed_args = []

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
        wrapped_f.will_fn_metadata["listener_regex"] = regex
        wrapped_f.will_fn_metadata["case_sensitive"] = case_sensitive
        wrapped_f.will_fn_metadata["multiline"] = multiline
        wrapped_f.will_fn_metadata["listens_only_to_direct_mentions"] = False
        wrapped_f.will_fn_metadata["listens_only_to_admin"] = admin_only
        wrapped_f.will_fn_metadata["listener_includes_me"] = include_me
        wrapped_f.will_fn_metadata["listens_to_messages"] = True
        wrapped_f.will_fn_metadata["listener_args"] = passed_args
        wrapped_f.will_fn_metadata["__doc__"] = f.__doc__

        return wrapped_f

    return wrap


def randomly(start_hour=0, end_hour=23, day_of_week="*", num_times_per_day=1):
    def wrap(f):

        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
        wrapped_f.will_fn_metadata["random_task"] = True
        wrapped_f.will_fn_metadata["start_hour"] = int(start_hour)
        wrapped_f.will_fn_metadata["end_hour"] = int(end_hour)
        wrapped_f.will_fn_metadata["day_of_week"] = day_of_week
        wrapped_f.will_fn_metadata["num_times_per_day"] = int(num_times_per_day)

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
            wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
            return wrapped_f
        return wrap


def require_settings(*setting_names):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
        wrapped_f.will_fn_metadata["required_settings"] = setting_names
        return wrapped_f
    return wrap


def route(path, *args, **kwargs):
    def wrap(f):
        f.will_fn_metadata = getattr(f, "will_fn_metadata", {})
        f.will_fn_metadata["bottle_route"] = path
        for k, v in kwargs.items():
            f.will_fn_metadata["bottle_%s" % k] = v
        return f
    return wrap
