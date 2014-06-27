# Creating and Organizing plugins

We've designed will to be able to scale from small, personal installs to big, corporate robots.  Here's how to get the most out of your plugins.


## Creating plugins

#### Where do plugins live?

Since plugins are just python files, they can live anywhere on the `PYTHONPATH`.  Will will look for plugins anywhere on the system `PYTHONPATH`, and automatically adds `will/plugins` and `your_will/plugins` to the path.


#### How do I specify which plugins to load?

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

#### What exactly is a plugin?

A plugins is just a python files with at least one class that subclasses `WillPlugin`, and at least one method that's decorated with [one of will's listen decorators](notice.md).

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


#### What does `WillPlugin` provide, exactly?

That's what the next section is all about.


## Included batteries

Will's `WillPlugin` class packs in lots of useful functionality to make writing powerful plugins simple.  Let's go through it.



#### Storage

Will can remember almost any python object (using [dill](https://pypi.python.org/pypi/dill)), even across reboots.

It's as simple as:

```python
self.save("my_key", "my_value")
self.load("my_key", "default value")
```



#### Template rendering

Will includes [Jinja](http://jinja.pocoo.org/) for powerful awesome template rendering.  To use it, just call `self.rendered_template()`


```python
self.rendered_template(template_name, context={})
```

- **`template_name`**: path to the template, relative to the `TEMPLATE_DIRS` specified in `config.py`.
- **`context`**: a dictionary to render the template with.

You can use `rendered_template()` directly in a plugin,

```python
@respond_to("what are the rooms\?")
def list_rooms(self, message):
    """what are the rooms?: List all the rooms I know about."""
    context = {"rooms": self.available_rooms.values(),}
    self.say(rendered_template("rooms.html", context), message=message, html=True)
```

Or, you can stack it as a decorator.

```python
@route("/")
@rendered_template("home.html")
def homepage_listener(self):
    return {}
```


#### Help and documentation

Just include a docstring, and your command will be included in @will help:


```python
class BonjourPlugin(WillPlugin):

    @respond_to("bonjour")
    def say_bonjour_will(self, message):
        """bonjour: I know how to say bonjour! In French!"""
        self.reply(message, "bonjour!")
```



#### Access settings and config

Will takes care of passing in environment variables and settings in the `settings module`.  To use it:

config.py:

```python
HELLO_MESSAGE = "Bonjour from config.py"
```

or, on the shell (note the `WILL_` prefix):

```bash
export WILL_HELLO_MESSSAGE="Bonjour from the environment"
```

then, in any plugin: 

```python
from will import settings

class BonjourPlugin(WillPlugin):

    @respond_to("bonjour")
    def say_bonjour_will(self, message):
        self.reply(message, settings.HELLO_MESSAGE)
```

You can also mark one or more settings as required for your plugin with the `require_settings` decorator, and they'll be checked on startup.

```python
from will import settings

class BonjourPlugin(WillPlugin):

    @require_settings("HELLO_MESSAGE", "ANOTHER_SETTING")
    @respond_to("bonjour")
    def say_bonjour_will(self, message):
        self.reply(message, settings.HELLO_MESSAGE)
```

When will starts up, he'll make sure they've been set:

![Verify settings](/img/verify_settings.gif)



#### Parse natural time

Often, it's useful to be able to talk to will about time in natural language.  To make that easy, will includes the helper functions built on [parsedatetime](https://github.com/bear/parsedatetime) and [natural](https://github.com/tehmaze/natural): `self.parse_natural_time` and `self.to_natural_day_and_time`.

##### parse_natural_time

`self.parse_natural_time(time_string)` parses a textual time string, and returns a `datetime` object.

```python
@respond_to("remind me on (?P<remind_time>.*)")
def remind_me_at(self, message, remind_time=None):
    parsed_time = self.parse_natural_time(remind_time)
```

![Parse natural time](/img/remind_trash.gif)


##### to_natural_day_and_time

`self.to_natural_day_and_time(my_datetime)` converts a python `datetime` into a human-friendly string.
```python
@respond_to("show_reminders")
def remind_me_at(self, message, remind_time=None):
    reminders = self.load("reminders")
    for r in reminders:
        natural_time = self.to_natural_day_and_time(r)
        self.say("On %s" % natural_time)
```



It's as simple as:

```python
self.save("my_key", "my_value")
self.load("my_key", "default value")
```


## Organizing plugins

If you have enough plugins, you may want to group them together by function.  Will makes this easy using modules.


#### What's a module?

A will module is just a python module: a folder with an `__init__.py`.

![Plugins folder with bonjour.py](/img/plugins_bonjour.gif)

That's it.

#### What about that awesome help text?

Glad you asked.  The help text comes from a special variable, expected to be in `__init__.py`: 

`__init__.py`


```
MODULE_DESCRIPTION = "Old-fashioned friendliness"
```

When help runs, plugins are grouped according to their `MODULE_DESCRIPTION`, which means you can have physically distinct modules that share the same help grouping.

![Both core and our will plugins, grouped](/img/core_vs_ours.gif)



Now you've got the hang of how to write your own plugins - but before you reinvent the wheel, take a look at [what plugins are included in will](bundled.md)!