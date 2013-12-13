
class PluginModulesLibraryMixin(object):

    @property
    def plugin_modules_library(self):
        print "plugin_modules_library"
        if not hasattr(self, "_plugin_modules_library"):
            try:
                if hasattr(self, "bot"):
                    self._plugin_modules_library = self.bot.load("plugin_modules_library", {})
                else:
                    self._plugin_modules_library = self.load("plugin_modules_library", {})
            except:
                import traceback; traceback.print_exc();
                return {}
        return self._plugin_modules_library
