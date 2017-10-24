class RosterMixin(object):

    def __init__(self, *args, **kwargs):
        import logging
        logging.critical(
            "RosterMixin has been moved to the hipchat backend.\n" +
            "Please change all your imports to `from will.backends.io_adapters.hipchat import HipChatRosterMixin`"
        )
        super(RosterMixin, self).__init__(*args, **kwargs)
