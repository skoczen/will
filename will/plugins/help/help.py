from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class HelpPlugin(WillPlugin):

    @respond_to("^help(?: (?P<plugin>.*))?$")
    def help(self, message, plugin=None):
        """help: the normal help you're reading."""
        selected_modules = help_modules = self.load("help_modules")

        self.say(f"Sure thing, {message.sender.handle}.", message, start_thread=True)

        help_text = "Here's what I know how to do:"
        if plugin and plugin in help_modules:
            help_text = f"Here's what I know how to do about {plugin}:"
            selected_modules = dict()
            selected_modules[plugin] = help_modules[plugin]
        self.say(help_text, start_thread=True)

        for k in sorted(selected_modules, key=lambda x: x[0]):
            help_data = selected_modules[k]
            if help_data:
                help_text = [f'```{k}']
                for line in help_data:
                    if line and ":" in line:
                        key, value = line.split(':', 1)
                        help_text.append(f"  {key}: {value}")
                self.say('\n'.join(help_text) + '```', message, start_thread=True)
