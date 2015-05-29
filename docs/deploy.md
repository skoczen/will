# Deploying your Will

Will's happy to run on your machine all day, every day.  But he really shines out in production where he can run independently of anything you do with your local machine.  Here are some best practices for deploying will.

## Deploy on Heroku

Heroku is our recommended platform for deployment because it's simple, easy, and free. That's a tough combination to beat.  You're in no way locked in to running will on heroku, though - run him wherever you want!

#### Step 1: Set up your heroku app, and a redis addon.

Assuming you have the [heroku toolbelt](https://toolbelt.heroku.com/) installed and all set up, it's as easy as this:
    
```bash
heroku create our-will-name
heroku addons:add rediscloud
```

A note on rediscloud: you can also use redistogo, openredis, or anyone else.  We use rediscloud and like them.


#### Step 2: Add all the needed environment variables:

You'll want to take all the variables that live in your virtualenv's `postactivate` file that feed into your will environment, and provide them to your heroku app.

At minimum, that's
```bash
heroku config:set \
WILL_PUBLIC_URL="http://our-will-name.herokuapp.com" \
WILL_USERNAME='12345_123456@chat.hipchat.com' \
WILL_PASSWORD='asj2498q89dsf89a8df' \
WILL_V2_TOKEN='asdfjl234jklajfa3azfasj3afa3jlkjiau' \
```

If you have more than 30 chat rooms, you must also set the V1 token to avoid hipchat rate limits:
```bash
heroku config:set WILL_V1_TOKEN='kjadfj89a34878adf78789a4fae3'
```

Finally, for will's schedule to be correct, you need to set him to the time zone you want:

```bash
heroku config:set TZ="America/Los_Angeles"
```

**Note:** You don't have to worry about setting the `REDIS_URL` or `HTTPSERVER_PORT`.  Will auto-detects those and takes care of it.

#### Step 3: Deploy!

You're all set to deploy your will. Ready? Go!


```bash
git push heroku
```

You app is now up on heroku.  Finally, turn it on!

`heroku scale web=1`

That should be it - head over to [http://our-will-name.herokuapp.com](http://our-will-name.herokuapp.com), and you should see will's smiling face.

If so, pop into chat, and give a:

![Hi, Hello, username!](img/hi_hello.gif)


#### Deploying future updates

Just commit your updates, then

```bash
git push heroku
```

Simple.  For best-practices, see our continuous deployment recommendations below.


## Deploy Everywhere Else

#### Will is Just Python

That says it all. Will is just python, and you can deploy him *anywhere* you have python, an open port, and access to redis.

In your chosen deploy environment and setup, you'll want to do a couple things:

#### Replicate your environment settings

At minimum, that's:
```bash
export WILL_PUBLIC_URL="http://our-will-name.herokuapp.com"
export WILL_USERNAME='12345_123456@chat.hipchat.com'
export WILL_PASSWORD='asj2498q89dsf89a8df'
export WILL_V2_TOKEN='asdfjl234jklajfa3azfasj3afa3jlkjiau'
export WILL_REDIS_URL='redis://some-domain.com/7/'
export WILL_HTTPSERVER_PORT='80'
```

If you have more than 30 chat rooms, you must also set the V1 token to avoid hipchat rate limits:
```bash
export WILL_V1_TOKEN='kjadfj89a34878adf78789a4fae3'
```

You'll also need to set any environment variables for your plugins.


#### Call run_will with something that handles restarts and crashes.

The command to kick off will is just:
```
python run_will.py
```

You can run that with whatever supervisory process you'd like. Will's very, very stable, but having something that handles crashes is still a pretty good idea.


#### Alternate approach

Ah, you say, but I have this crazy python-twisted-zope-node monolith that self-repairs mars and can do everything. Why do I need the shell at all?

Answer, crazy monolith mars person: you don't.  Will is Just Python.

```python
from will.main import WillBot

bot = WillBot()
bot.bootstrap()
```

and you're good.


## Storage Backends

Will's default storage backend is Redis, but he supports some others if you can't run Redis.

To change the backend, just set `STORAGE_BACKEND` in `config.py` and then supply any other needed settings for the new storage backend.  The currently supported backends are:

 * `redis` - The default Redis backend
 * `couchbase` - A Couchbase backend
 * `file` - Keeps the settings as files on a local filesystem


#### Couchbase

Couchbase requries you set `COUCHBASE_URL` in your config.

You are also required to have the python Couchbase client (and thus, libcouchbase) installed.  If you are installing for development you can use `pip install -r requirements.couchbase.txt` to pull in the Couchbase client.  See [the Python Couchbase client repo](https://github.com/couchbase/couchbase-python-client) for more info.

Examples:

 * `COUCHBASE_URL='couchbase:///bucket'`
 * `COUCHBASE_URL='couchbase://hostname/bucket'`
 * `COUCHBASE_URL='couchbase://host1,host2/bucket'`
 * `COUCHBASE_URL='couchbase://hostname/bucket?password=123abc&timeout=5'`

#### File

File requires you set `FILE_DIR` in your config to point to an empty directory.

Examples:

 * `FILE_DIR='/var/run/will/settings/'`
 * `FILE_DIR='~will/settings/'`


## Best Practices

In this section, we describe how we deploy and host will, in the hopes that others come forward and share what's working for them, too.  The more good practices, the better.

#### Our Stack

We host on heroku, using rediscloud for redis, mailgun for email, and things have been peachy.  We deploy via CD using CircleCI. Details on that below.

#### Use Continuous Deployment

Our stack is set up so that any pushes on will's master branch have tests run on [CircleCI](http://circleci.com), and if they pass, a new version is deployed to heroku immediately.  This has been delightful. Even though will has very, very minimal tests, we generally catch if things are horribly broken, and it's meant that adding new functionality to will takes minutes, sometimes seconds of developer time.

Continuous Deployment has dramatically changed how we build and use will - instead of talking about "what if will did...", generally, people just implement it, push it, and play with it for real.  It's been a great place to be.  It might be for you too.

That's it in getting your will up and running!   But maybe you're one of those people who wants to pitch in and make will even better. Awesome. Learn [how to improve will](improve.md).


