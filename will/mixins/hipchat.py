class HipChatMixin(object):

    def __init__(self, *args, **kwargs):
        import logging
        logging.critical(
            "HipChatMixin functionality has been moved to the hipchat backend.\n" +
            "If you need functionality that used to be on this class, please either\n" +
            "publish messages, or use will.backends.io_backends.hipchat:HipChatBackend."
        )
        super(HipChatMixin, self).__init__(*args, **kwargs)
