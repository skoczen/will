# Configuring Will

Most of will's configuration is done interactively, using `run_will.py`, or specifying via the plugins.  There are, however a few built-in settings and config worth covering.  We'll aim to address all of them here.

## Environment variables

All environment variables prefixed with `WILL_` are imported into will's `settings` modules.

In best practices, you should keep all of the following in environment variables:

- `WILL_SLACK_API_TOKEN`
- `WILL_HIPCHAT_USERNAME`
- `WILL_HIPCHAT_PASSWORD`
- `WILL_HIPCHAT_V2_TOKEN`
- `WILL_HIPCHAT_V1_TOKEN`
- `WILL_ROCKETCHAT_USERNAME`
- `WILL_ROCKETCHAT_PASSWORD`
- `WILL_ROCKETCHAT_URL`
- `WILL_REDIS_URL`
- Any other tokens, keys, passwords, or sensitive URLS.

We've made it easy.  No excuses. :)

## config.py

Config.py is where all of your non-sensitive settings should go.   This includes things like:

- `PLUGINS`: The list of plugins to run,
- `PLUGIN_BLACKLIST`: The list of plugins to ignore, even if they're in `PLUGINS`,
- `IO_BACKENDS`: The list services you want Will to connect to,
- `ANALYZE_BACKENDS`: The list of message-analysis backends you want Will to run through.
- `GENERATION_BACKENDS`: The list of reply-generation backends you want Will to go through.
- `EXECUTION_BACKENDS`: The list of decision-making and execution backends you want Will to go through (we recommend just having one.)
- `STORAGE_BACKEND`: Which backend you'd like to use for Will to store his long-term memory. (Built-in: 'redis', 'couchbase', 'file')
- `PUBSUB_BACKEND`: Which backend you'd like to use for Will to use for his working memory. (Built-in: 'redis'.  Soon: 'zeromq', 'builtin')
- `ENCYPTION_BACKEND`: Which backend you'd like to use for Will to encrypt his storage and memory. (Built-in: 'aes'.)
- `PUBLIC_URL`: The publicly accessible URL will can reach himself at (used for [keepalive](plugins/bundled.md#administration)),
- `HTTPSERVER_PORT`: The port will should handle HTTP requests on.  Defaults to 80, set to > 1024 if you don't have sudo,
- `REDIS_MAX_CONNECTIONS`: The maximum number of connections to make to redis, for connection pooling.
- `FUZZY_MINIMUM_MATCH_CONFIDENCE`:  What percentage of confidence Will should have before replying to a fuzzy match.
- `FUZZY_REGEX_ALLOWABLE_ERRORS`:  The maximum number of letters that can be wrong in trying to make a fuzzy match.
- `SLACK_DEFAULT_CHANNEL`: The default Slack channel to send messages to (via webhooks, etc)
- `HIPCHAT_ROOMS`: The list of rooms to join,
- `HIPCHAT_DEFAULT_ROOM`: The room to send messages that come from web requests to,
- `DEFAULT_BACKEND`: The service to send messages that come from web requests to,
- `TEMPLATE_DIRS`: Extra directories to look for templates,
- `ADMINS`: The mention names of all the admins,
- `LOGLEVEL`: What logging level to use,
- `HIPCHAT_SERVER`: if you're using the [HipChat server beta](https://www.hipchat.com/server), the hostname of the server,
- `ALLOW_INSECURE_HIPCHAT_SERVER`: the option to disable SSL checks (seriously, don't),
- `ENABLE_INTERNAL_ENCRYPTION`: the option to turn off internal encryption (not recommended, but you can do it.)
- `PROXY_URL`: Proxy server to use, consider exporting it as `WILL_PROXY_URL` environment variable, if it contains sensitive information
- and all of your non-sensitive plugin settings.


More expansive documentation on all of those settings is in `config.py`, right where you need it.

## How environment variables and config.py are combined

The environment variables and config.py are combined, and made available to the rest of the app at:

```python
from will import settings

print settings.MY_SETTING_NAME
```

The rules for combining are fairly straightforward:

1. All environment variables that start with `WILL_` are imported, and `WILL_` is stripped off their name. (i.e. `WILL_PORT` becomes `PORT`)
2. All variables from `config.py` are imported.  If there is a conflict, `config.py` wins, and a message is displayed:

    ![Config Conflict](img/config_conflict.gif)

3. Some smart defaulting happens inside settings.py for important variables.  For the moment, I'm going to leave that out of the docs, and refer you to `settings.py` as I *believe* things should Just Work, and most people should never need to care.  If this decision's wrong, please open an issue, and these docs will be improved!

That's it for config.  Now, you can either do a deeper dive into [Will's brain](/backends/overall.md), or just get your will [deployed](deploy.md)!



