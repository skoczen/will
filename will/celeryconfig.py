from celery import Celery
import settings

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

app = Celery('will', broker=settings.WILL_REDIS_URL)


