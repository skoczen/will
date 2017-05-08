# Creating and Organizing plugins

We've designed will to be able to scale from small, personal installs to big, corporate robots.  Here's the best practices on creating and organizing your plugins.

## Where do plugins live?

Since plugins are just python files, they can live anywhere on the `PYTHONPATH`.  Will will look for plugins anywhere on the system `PYTHONPATH`, and automatically adds `will/plugins` and `your_will/plugins` to the path.


## How do I specify which plugins to load?

The list of plugins to load lives in `config.py`, as well as a blacklist of plugins that, even if they're on the path, should be ignored.

When given a module, will imports it, then *recursively loads* all plugins found within it.

Both `PLUGINS` and `PLUGINS_BLACKLIST` can contain:

Built-in will plugins, e.g.:

- All built-in modules: `will.plugins`
- Built-in modules: `will.plugins.module_name`
- Specific plugins: `will.plugins.module_name.plugin`

Plugins in your will, e.g.:

- All modules: `plugins`
- A specific module: `plugins.module_name`
- Specific plugins: `plugins.module_name.plugin`

Plugins anywhere else on your PYTHONPATH, e.g.:

- All modules: `someapp`
- A specific module: `someapp.module_name`
- Specific plugins: `someapp.module_name.plugin`


Here's the corresponding section of `config.py`, by default:

```python
PLUGINS = [
    # Built-ins
    "will.plugins.admin",
    "will.plugins.chat_room",
    "will.plugins.devops",
    "will.plugins.friendly",
    "will.plugins.help",
    "will.plugins.productivity",
    "will.plugins.web",

    # All plugins in your project.
    "plugins",
]

# Don't load any of the plugins in this list.  Same options as above.
PLUGIN_BLACKLIST = [
    # "will.plugins.friendly.cookies",      # But who would deprive will of cookies??
]
```

## What exactly is a plugin?

A plugin is just a python file with at least one class that subclasses `WillPlugin`, and at least one method that's decorated with [one of will's listen decorators](notice.md).

For example:

ping.py

```
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class PingPlugin(WillPlugin):

    @respond_to("^ping$")
    def ping(self, message):
        self.reply(message, "PONG")
```


## What's a module?

Modules are a way to group similar plugins.

Structurally, a will module is just a python module: a folder with an `__init__.py`.

![Plugins folder with bonjour.py](../img/plugins_bonjour.gif)

That's it.

## What about that awesome help text?

Glad you asked.  The help text comes from a special variable, expected to be in `__init__.py`: 

`__init__.py`


```
MODULE_DESCRIPTION = "Old-fashioned friendliness"
```

When help runs, plugins are grouped according to their `MODULE_DESCRIPTION`, which means you can have physically distinct modules that share the same help grouping.

![Both core and our will plugins, grouped](../img/core_vs_ours.gif)



Easy, right?  Awesome. Now that you know where to put them, take a look at the [built-in features on WillPlugin](builtins.md).

