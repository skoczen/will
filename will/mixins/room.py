
class Room(object):

    def __init__(self, *args, **kwargs):
        import logging
        logging.critical(
            "Room has been renamed to HipChatRoom, and will be removed from future releases.\n" +
            "Please change all your imports to will.backends.io_adapters.hipchat import HipChatRoom"
        )
        super(Room, self).__init__(*args, **kwargs)


class RoomMixin(object):

    def __init__(self, *args, **kwargs):
        import logging
        logging.critical(
            "RoomMixin has been renamed to HipChatRoomMixin, and will be removed from future releases.\n" +
            "Please change all your imports to will.backends.io_adapters.hipchat import HipChatRoomMixin"
        )
        super(RoomMixin, self).__init__(*args, **kwargs)
