import requests

from will import settings
from will.decorators import require_settings
from .base import ExecutionBackend

class AllBackend(ExecutionBackend):

    def execute(self, message):
        print "in execution"
        print message
        print "do stuff"
        return {}
