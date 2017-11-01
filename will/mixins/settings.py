from clint.textui import colored, puts, indent
from will import settings
from will.utils import show_valid, warn, error


class SettingsMixin(object):
    required_settings = []

    def verify_setting_exists(self, setting_name, message=None):
        from will import settings

        if not hasattr(settings, setting_name):
            self.say("%s not set." % setting_name, message=message)
            return False
        return True

    def verify_settings(self, quiet=False):
        passed = True
        for s in self.required_settings:
            if not hasattr(settings, s["name"]):
                meta = s
                if hasattr(self, "friendly_name"):
                    meta["friendly_name"] = self.friendly_name
                else:
                    meta["friendly_name"] = self.__class__.__name__
                if not quiet:
                    with indent(2):
                        error("%(name)s is missing. It's required by the %(friendly_name)s backend." % meta)
                        with indent(2):
                            error_message = (
                                "To obtain a %(name)s: \n%(obtain_at)s"
                            ) % meta
                            puts(error_message)
                passed = False
                # raise Exception(error_message)
            else:
                if not quiet:
                    with indent(2):
                        show_valid(s["name"])
        if not passed:
            raise EnvironmentError(
                "Missing required settings when starting up %s."
                "Please fix the error above and restart Will!" % (meta["friendly_name"], )
            )
        return passed
