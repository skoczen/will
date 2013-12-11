
class SettingsMixin(object):

    def verify_setting_exists(self, setting_name, message=None):
        from will import settings

        if not hasattr(settings, setting_name):
            self.say("%s not set." % setting_name, message=message)
            return False
        return True
