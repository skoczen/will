# How will can respond

Will can notice a variety of things, and this list keeps growing.  When you want your will to pay attention to a particular thing, you'll use one of will's decorators - an example of each is below.


## Talk to the room

Filler - Simple enough - if you directly @will mention him in a message, he'll see these.  It's exactly what we used in the hello, world example.

```
@respond_to("bonjour")
def say_bonjour_will(self, message):
    # Awesome stuff
```

`@respond_to` takes a number of options:

```
@respond_to(regex, include_me=False, case_sensitive=False, multiline=False, admin_only=False)
```

- **regex**: a regular expression to match.
- **include_me**: whether will should include the things he says as possible matches
- **case_sensitive**: should the regex be case sensitive?
- **multiline**: should the regex allow multiline matches?
- **admin_only**: only runs the command if the sender is specified as an administrator.

&nbsp; 

- How will can respond
    - Talk to the room
    - Reply to a person
    - Say something in the future
    - Talk to the room from a webhook
    - Send an email
    - Do any python thing
        - API endpoint
        - etc
    - PRs welcome (sms, etc)
