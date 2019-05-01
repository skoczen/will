from plugins.pco import msg_attachment
import logging


def get_slack_channel_link(will, new_channel):
    """Retrieves a slack formatted link from a channel name. This should probably be moved somewhere else."""
    channels = will.load("slack_channel_cache")
    channel = None
    for key in channels:
        # print(channels[key])
        if channels[key]['name'] == new_channel.strip(' '):
            # print(channels[key]['name'])
            channel = "<#%s|%s>" % (channels[key]['id'], channels[key]['name'])
    return channel


def announcement_channel(will):
    """Used for retrieving the current announcement channel"""
    if will.load('announcement_channel'):
        channel = will.load('announcement_channel')
    else:
        will.save('announcement_channel', 'announcements')
        channel = 'announcements'
    return channel


def initialize_announcement_toggles(will):
    announcement_toggles = {'birthdays': True,
                            'new_person_created': True,
                            'live_service_update': True}
    will.save('announcement_toggles', announcement_toggles)
    will.reply('Initilized Toggles!\n', attachments=get_toggles(will))
    return announcement_toggles


def get_toggles(will):
    """Returns a string formated list of current announcement toggles"""
    announcement_toggles = will.load('announcement_toggles')
    toggle_msg = "\nCurrent Announcement Toggles:\n"
    for toggle, value in announcement_toggles.items():
        toggle_msg += ": ".join([toggle.replace("_", " ").title(),
                                 str(value).replace('False', 'Off').replace('True', 'On') + "\n"])
    toggle_attachment = msg_attachment.SlackAttachment(fallback=toggle_msg,
                                                       text=toggle_msg)
    return toggle_attachment.slack()


def announcement_is_enabled(will, announcement):
    is_enabled = True
    if will.load('announcement_toggles'):
        announcement_toggles = will.load('announcement_toggles')
        try:
            is_enabled = announcement_toggles[announcement]
        except KeyError:
            logging.info("Couldn't find this announcement toggle so letting it pass.")
    else:
        will.initialize_announcement_toggles()

    return is_enabled
