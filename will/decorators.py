from celery.task.schedules import crontab
from bottle import route, run, template



def respond_to(regex, include_me=False):
    def wrap(f):
        passed_args = []
        def wrapped_f(*args):
            passed_args = args
            f(*args)
        wrapped_f.listener_regex = regex
        wrapped_f.listens_only_to_direct_mentions = True
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        wrapped_f.listener_args = passed_args
        return wrapped_f

    return wrap


def scheduled(run_every):
    def wrap(f):
        def wrapped_f(*args):
            f(*args)
        return wrapped_f
    return wrap

def one_time_task(when):
    def wrap(f):
        def wrapped_f(*args):
            f(*args)
        return wrapped_f
    return wrap

def hear(regex, include_me=False):
    def wrap(f):
        passed_args = []
        def wrapped_f(*args):
            passed_args = args
            f(*args)
        wrapped_f.listener_regex = regex
        wrapped_f.listens_only_to_direct_mentions = False
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        wrapped_f.listener_args = passed_args
        return wrapped_f
    
    return wrap


def randomly(start_hour=0, end_hour=23, weekdays_only=False):
    def wrap(f):
        def wrapped_f(*args):
            f(*args)
        return wrapped_f
    return wrap


def rendered_template(template_name, context=None):
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('will', 'templates'))
    if context is not None:
        template = env.get_template(template_name)
        return template.render(**context)
    else:
        def wrap(f):
            def wrapped_f(*args):
                context = f(*args)
                if type(context) == type({}):
                    template = env.get_template(template_name)
                    return template.render(**context)
                else:
                    return context
            return wrapped_f
        return wrap

crontab = crontab
