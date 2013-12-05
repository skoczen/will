from celery.task.schedules import crontab
from bottle import route, run, template


def respond_to(regex, include_me=False):
    print "respond_to %s" % regex
    def wrap(f):
        def wrapped_f(*args):
            # print "Decorator arguments:", regex
            f(*args)
        wrapped_f.respond_to = regex
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        return wrapped_f

    return wrap


def scheduled(run_every):
    def wrap(f):
        def wrapped_f(*args):
            # print "Decorator arguments:", regex
            f(*args)
        return wrapped_f
    return wrap

def one_time_task(when):
    def wrap(f):
        def wrapped_f(*args):
            # print "Decorator arguments:", regex
            f(*args)
        return wrapped_f
    return wrap

def hear(regex, include_me=False):
    def wrap(f):
        def wrapped_f(*args):
            # print "Decorator arguments:", regex
            f(*args)
        wrapped_f.listener_regex = regex
        wrapped_f.listener_includes_me = include_me
        wrapped_f.listens_to_messages = True
        return wrapped_f
    
    return wrap


def randomly(start_hour=0, end_hour=23, weekdays_only=False):
    def wrap(f):
        def wrapped_f(*args):
            # print "Decorator arguments:", 
            f(*args)
        return wrapped_f
    return wrap

crontab = crontab
