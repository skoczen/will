# Teach your will awesome stuff

Your will is all yours.  He'll come with all the great functions of the will library, but the power to teach him the things that are really useful to you is completely in your hands.

We've designed will to be the friendliest, easiest-to-teach bot anywhere, where even non-coders can hop in and add new functionality in a matter of minutes.  We hope you'll find him as friendly as we do!

---

## Plugin basics

Plugins are just normal python files with at least one class that subclasses `WillPlugin`, and at least one method that's decorated. They can live anywhere normal python modules live, and will has some niceties to make organizing them simple.

But sometimes, the best way to learn is to dive right in - so let's make one!


## Hello, world

Let's start as simple as they come - a plugin for will to say hello.  Since he already comes with "hello", and "hi", in this example, we'll go with "bonjour!"

#### Step 1: Create a bonjour.py

This file can be called anything, but given the functionality, bonjour seems like a fair name.  Create the file in your plugins folder:

![Plugins folder with bonjour.py](../img/plugins_bonjour.gif)

#### Step 2: Add the plugin python code

In the `bonjour.py` file, add this:

```python
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class BonjourPlugin(WillPlugin):

    @respond_to("bonjour")
    def say_bonjour_will(self, message):
        """bonjour: I know how to say bonjour! In French!"""
        self.reply(message, "bonjour!")


```

#### Step 3: Restart your will

Finally, `ctrl+c` then restart your will to load the new plugin, and you should be able to do this:

![Plugins folder with bonjour.py](../img/bonjour_chat.gif)

Easy, right?  Well, now that you've got your feet wet, let's see  [what else will knows how to notice](notice.md).
