# Whitelist allows you to configure a list of channels that are whitelisted.
# Use this to control what commands are allowed to run in a channel
import logging


# Initilizes a whitelist if none exists
def whitelist_init(will):
    whitelist = []
    will.save("whitelist", whitelist)
    return


# This cleans the whitelist, and then lists the channels.
def whitelist_list(will):
    try:
        white_list = whitelist_clean(will)
    except TypeError:
        logging.info("No whitelist to list, we'll make an empty one.")
        whitelist_init(will)
        white_list = []
    finally:
        if white_list:
            response = get_slack_channels(will, white_list)
            will.reply("Sending you the whitelist as a direct message.")
            will.say("This is the whitelist: %s" % response, channel=will.message.data.sender.id)
        else:
            will.reply("The whitelist is empty.")

        return


# This removes duplicates from the whitelist,
# and removes DM channels from the whitelist since they're already whitelisted by default.
def whitelist_clean(will):
    white_list = will.load("whitelist")
    white_list = list(set(white_list))
    for entry in white_list:
        if entry.startswith('D'):
            white_list.remove(entry)
    will.save("whitelist", white_list)
    return white_list


# Removes channel(s) from the whitelist returns replies to the channel that it is removed.
# Requires WILLPlugin object, and optionally a channel name.
# If no channel names are given it removes the channel the event came from.
def whitelist_remove(will, channel_name=None):
    if channel_name:
        channel_name = channel_name.strip()
        channel_id = get_slack_chan_ids(will, channel_name.split())
    else:
        channel_id = will.message.data.channel.id.split()
        channel_name = will.message.data.channel.name
    try:
        if not channel_id:
            will.reply('I coulnd\'t find a channel named "%s"' % channel_name)
        else:
            white_list = will.load("whitelist")
            for c_id in channel_id:
                white_list.remove(c_id)
            will.save("whitelist", white_list)
            will.reply('"%s" channel(s) removed from the whitelist.' % channel_name)
    except Exception as e:
        logging.info(type(e))
    return


# Adds channel(s) to the whitelist and returns to the channel that it has been added.
# Requires WILLPlugin object, and optionally a channel name.
# If no channel names are given it adds the channel the event came from.
def whitelist_add(will, channel_name=None):
    if channel_name:
        channel_name = channel_name.strip()
        channel_id = get_slack_chan_ids(will, channel_name.split())
    else:
        channel_id = will.message.data.channel.id.split()
        channel_name = will.message.data.channel.name
    try:
        if not channel_id:
            will.reply('I coulnd\'t find a channel named "%s"' % channel_name)
        else:
            try:
                white_list = will.load("whitelist")
            except:
                white_list = []
            finally:
                for c_id in channel_id:
                    white_list.append(c_id)
                will.save("whitelist", white_list)
                will.reply('"%s" channel(s) added to the whitelist.' % channel_name)
    except Exception as e:
        logging.info(type(e))
    return


# Returns the channel id the event came in on if that channel is whitelisted.
# Otherwise it returns the Slack DM channel for that user.
# Use this with custom plugins so will will respond privately if the room is not whitelisted.
def wl_chan_id(will):
    channel = ""
    try:
        whitelist = will.load("whitelist")
        if will.message.data.channel.id not in whitelist and not will.message.data.channel.id.startswith("D"):
            will.reply('The "%s" channel is not whitelisted. So I sent it as a direct message.'
                       % will.message.data.channel.name.title())
            channel = will.message.data.sender.id
        else:
            channel = will.message.data.channel.id
    except TypeError:
        msg = ""
        if will.message.data.channel.id.startswith("D"):
            msg = 'Whitelist Initialized'
        else:
            msg = 'Whitelist Initialized\nThe "%s" channel is not whitelisted. So I sent it as a direct message.' \
                  % will.message.data.channel.name.title()
        channel = will.message.data.sender.id
        whitelist_init(will)
        will.reply(msg)
    finally:
        return channel


# Returns True or false if the channel the event came in on is in the whitelist
def wl_check(will):
    result = False
    try:
        whitelist = will.load("whitelist")
        if will.message.data.channel.id not in whitelist:
            will.reply('Sorry the "%s" channel is not whitelisted.'
                       % will.message.data.channel.name.title())
            result = False
        else:
            result = True
    except Exception as e:
        will.reply("Exception: %s" % type(e))
    finally:
        return result


# This looks up the channel ID's in the whitelist and returns the corresponding slack channel name.
# This is so our channel names are always up to date.
def get_slack_channels(will, id_list):
    channel_cache = will.load('slack_channel_cache', {})
    channel_names = []
    for k, c in channel_cache.items():
        for id in id_list:
            if id in k:
                channel_names.append(c.name)
    return channel_names


# This looks up the channel names in the whitelist and returns the corresponding slack channel ID.
# This is so our channel names are always up to date.
def get_slack_chan_ids(will, channel_names):
    channel_cache = will.load('slack_channel_cache', {})
    channel_ids = []
    for k, c in channel_cache.items():
        for name in channel_names:
            if name in c.name:
                channel_ids.append(k)
    return channel_ids


# This looks up the channel IDs in the whitelist and returns the channel ids that have no members
# This signifies that a channel has been archived.
def get_slack_archived_channels(will, id_list):
    channel_cache = will.load('slack_channel_cache', {})
    channel_ids = []
    for k, c in channel_cache.items():
        for id in id_list:
            if id in k:
                if not c.members:
                    channel_ids.append(c.id)
    return channel_ids


def whitelist_wipe(will):
    try:
        will.clear("whitelist")
    except Exception as e:
        logging.info("There isn't a whitelist to clear.")
        will.reply("There isn't a whitelist to clear.")
    finally:
        return
