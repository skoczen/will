from will import settings


class IOBackend(object):
    is_will_iobackend = True

    def send_direct_message(self, *args, **kwargs):
        # This needs to recieve the message and context, and is what's responsible
        # for returning the reply along the proper IO channel

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.send_direct_message(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.send_direct_message(*args, **kwargs)

    def send_direct_message_reply(self, *args, **kwargs):

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.send_direct_message_reply(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.send_direct_message_reply(*args, **kwargs)

    def send_room_message(self, *args, **kwargs):

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.send_room_message(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.send_room_message(*args, **kwargs)


    def set_room_topic(self, *args, **kwargs):

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.set_room_topic(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.set_room_topic(*args, **kwargs)

    def get_user(self, *args, **kwargs):

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.get_hipchat_user(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.get_user(*args, **kwargs)

    @property
    def get_user_list(self, *args, **kwargs):

        if "hipchat" in settings.CHAT_BACKENDS:
            b = HipChatBackend()
            b.full_hipchat_user_list(*args, **kwargs)

        if "shell" in settings.CHAT_BACKENDS:
            b = ShellBackend()
            b.full_hipchat_user_list(*args, **kwargs)

    def get_room_list(self, *args, **kwargs):
        pass

    def handle_message(message, context, *args, **kwargs):
        context.platform = ""

        pass