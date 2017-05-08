# Tentative APK thoughts


```python

from will import events, io

class IOBackend():
    # Input and Output for modes of communication (Slack, SMS, HipChat, HTTP, etc)

    def init():
        # Authenticates with any service, checks settings, prepares the service, and emits an "init_complete" event.
        events.emit("init_complete", "IOName")

    def direct_message():
        pass

    def hear():
        pass

    def say():
        pass


class SkillBackend():
    # Things will can know how to do, available to any AIOS app.
    name = "MySkill"
    namespace = "myskill"

    def init():
        # Authenticates, checks settings, prepares the service, and emitsn "init_complete" event.
        events.emit("init_complete", "SkillName")

    def do_stuff(*args, **kwargs):
        # This method is exported as will.myskill.do_stuff
        pass


class ParsingBackend():
    # Takes an input, looks through the list of things will knows about, and decides what (if anything) to do.

    def __init__():
        pass

    def handle_input(message, context, knowledge):
        pass


class AIOSApp(*args, **kwargs):
    # The base class for AIOS apps (currently: plugins)
    name = "mycoolapp"

    def __init__(*args, **kwargs):
        # Some magical hooks to make sure context and replies Just Work TM.
        pass

    @hear("thing/regex")
    def do_stuff(messsage, context):
        io.reply("Cool")


    @public
    def method_other_apps_can_call(messsage, context):
        # Callable via will.apps.mycoolapp.method_other_apps_can_call
        return "stuff I did"

    @requestable("Access to my calendar")
    def method_other_apps_can_ask_permission_for(*args, **kwargs)
        # Callable if the user has allowed another app to have access to this app.
        return "stuff only some people can know"
        
```


Structure:

app.py
tests.yml (?  py?)  - Would love to see a conversation here.

Me:  Will, image me ___ 
Will:  Sure thing!  <image>




Bigger community support:

- Support hubot plugins?
- Support WP themes?