# How will can respond

Will can respond in a variety of ways, and since he's pure python, your imagination is the limit.


## Talk to the room

Like any normal person, will can talk to the chat room, or in 1-1 chats.  To talk to the room in your plugins, you'll want to use the `self.say()` method.

```python
@respond_to("bonjour")
def say_bonjour_will(self, message):
    # Awesome stuff
    self.say("Bonjour!", message=message)
```

![Bonjour!](../img/only_bonjour.gif)

Note that we pass `messsage` along.  This allows will to route his reply to the correct room.  Without it, he'll just speak to the `DEFAULT_ROOM`.

`say()` comes with a number of options, including color, html, and ping notify. 

```python
self.say(content, message=None, room=None, html=False, color="green", notify=False)
```

- **`content`**: the content you want to send to the room. Any string will do, HTML or plain text.
- **`message`**: (optional) The incoming message object
- **`room`**: (optional) The room object (from self.available_rooms) to send the message to.
- **`html`**: if the message is HTML. `True` or `False`.
- **`color`**: (chat room only) the hipchat color to send. "yellow", "red", "green", "purple", "gray", or "random". Default is "green". 
- **`notify`**: whether the message should trigger a 'ping' notification. `True` or `False`.

## Reply with a mention

Sometimes you want will to ping you - that's where @name mentions are great.  To do those in will, you'll want to use `self.reply()`

```python
@respond_to("^hi")   # Basic
def hi(self, message):
    self.reply(message, "hello, %s!" % message.sender.nick)
```

![Hi, Hello, username!](../img/hi_hello.gif)

Note the order of arguments is different here, and `messsage` is required. All the options: 

```python
self.reply(message, content, html=False, color="green", notify=False)
```

- **`message`**: The incoming message object.  Required
- **`content`**: the content you want to send to the room. HTML or plain text.
- **`html`**: if the message is HTML. `True` or `False`.
- **`color`**: (chat room only) the hipchat color to send. "yellow", "red", "green", "purple", "gray", or "random". Default is "green".
- **`notify`**: whether the message should trigger a 'ping' notification. `True` or `False`.



## Talk to the room from a webhook

When will recieves messages from webhooks and HTTP requests, he's still connected to chat, and you can use `.say()`. By default, he'll speak to `DEFAULT_ROOM`.

```python
@route("/ping")
def ping(self):
    self.say("PONG!")
```

If you want to talk to a different room, you can pass in the `room` argument with one of the rooms from `self.available_rooms`.


## Send an email

Will has one email backend at the moment, via [mailgun](http://www.mailgun.com).  If you've set `DEFAULT_FROM_EMAIL`, `MAILGUN_API_URL`, and `MAILGUN_API_KEY`, you can use `self.send_email()`

```python
@respond_to("status report")
def send_status_report(self):
    self.send_email(email_list=['jill@example.com'], subject="Here's the latest report", message=rendered_template("report.html", {}))
```

Here's all the options:

```python
self.send_email(from_email=None, email_list=[], subject="", message="")
```

- **`from_email`**: (Optional) The email address the message should come from. Defaults to `DEFAULT_FROM_EMAIL`.
- **`email_list`**: The list of addresses to send to.
- **`subject`**: (Optional) The email subject.
- **`message`**: (Optional) The email body.


## Schedule a reply for the future

Sometimes, you want will to make plans for the future.  That's where `self.schedule_say()` comes in handy.


```python
@randomly(start_hour='10', end_hour='17', day_of_week="mon-fri", num_times_per_day=1)
def walkmaster(self):
    now = datetime.datetime.now()
    in_5_minutes = now + datetime.timedelta(minutes=5)

    self.say("@all Walk happening in 5 minutes!")
    self.schedule_say("@all It's walk time!", in_5_minutes)
```

The options are pretty much the same as `self.say`, with the addition of the `when` parameter.

```python
self.schedule_say(content, when, message=None, room=None, html=False, color="green", notify=False)
```

- **`content`**: the content you want to send to the room. Any string will do, HTML or plain text.
- **`when`**: when you want the message to be said. Python `datetime` object.
- **`message`**: (optional) The incoming message object
- **`room`**: (optional) The room object (from self.available_rooms) to send the message to.
- **`html`**: if the message is HTML. `True` or `False`.
- **`color`**: (chat room only) the hipchat color to send. "yellow", "red", "green", "purple", "gray", or "random". Default is "green".
- **`notify`**: whether the message should trigger a 'ping' notification. `True` or `False`.


## Set the topic

Sometimes, it's good to give the conversation some direction.  Will can set the topic in hipchat using `self.set_topic()`

```python
import requests

@respond_to("new topic")
def give_us_somethin_to_talk_about(self, message):
    r = requests.get("http://chatoms.com/chatom.json?Normal=1&Fun=2&Philosophy=3&Out+There=4")
    data = r.json()
    self.set_topic(data["text"], message=message)
```

Note: you can't set the topic of a 1-1 chat. Will will complain politely.  All options:

```python
self.set_topic(topic, message=None, room=None) 
```

- `topic`: The string you want to set the topic to
- `message`: (optional) The incoming message object
- `room`: (optional) The room object (from self.available_rooms) to send the message to.



## Do any python thing

Will is Just Python.  Because of that, your imagination is the limit of what he can do to respond to requests.

Here's a few things our will does, every day:

- Spins up and tears down staging stacks,
- Monitors uptime on our production sites, and contacts the on-call developer if things go down,
- Keeps track of code reviews on pending branches,
- Add new signups to our CRM,
- Starts our daily standup video chat,
- And the list goes on.

Will is open-source, and PRs are very welcome.  If someone wants to write `self.send_sms()`, or anything else, it's all yours!

Ready to make some plugins?  Check out [how to create and organize plugins](create.md).
