import logging
import traceback


class PluginModulesLibraryMixin(object):

    @property
    def plugin_modules_library(self):
        if not hasattr(self, "_plugin_modules_library"):
            try:
                if hasattr(self, "bot"):
                    self._plugin_modules_library = self.bot.load("plugin_modules_library", {})
                else:
                    self._plugin_modules_library = self.load("plugin_modules_library", {})
            except:
                logging.critical("Error loading plugin_modules_library: \n%s", traceback.format_exc())
                return {}
        return self._plugin_modules_library
