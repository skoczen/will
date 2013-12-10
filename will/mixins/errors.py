import logging
import traceback

class ErrorMixin(object):
    def get_startup_errors(self):
        if hasattr(self, "_startup_errors"):
            return self._startup_errors
        return []

    def startup_error(self, error_message, exception_instance):
        error_message = "%s%s" % (
            error_message,
            ":\n\n%s\nContinuing...\n" % traceback.format_exc(exception_instance)
        )
        if not hasattr(self, "_startup_errors"):
            self._startup_errors = []
        self._startup_errors.append(error_message)
        logging.critical(error_message)

    def runtime_error(self, error_message):
        logging.critical(error_message)        