
class WillPlugin(object):
    is_will_plugin = True

    def say(self, message, html=True):
        print "say: %s" % message