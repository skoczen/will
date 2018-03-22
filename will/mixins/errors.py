import logging
import traceback


class ErrorMixin(object):
    def get_startup_errors(self):
        if hasattr(self, "_startup_errors"):
            return self._startup_errors
        return []

    def add_startup_error(self, error_message):
        if not hasattr(self, "_startup_errors"):
            self._startup_errors = []
        self._startup_errors.append(error_message)

    def startup_error(self, error_message, exception_instance):
        traceback.print_exc()
        error_message = "%s%s" % (
            error_message,
            ":\n\n%s\nContinuing...\n" % traceback.format_exc(exception_instance)
        )
        self.add_startup_error(error_message)
        logging.critical(error_message)

    def runtime_error(self, error_message):
        logging.critical(error_message)
