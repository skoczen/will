from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template
from will import settings

class CleanAWSBucketsPlugin(WillPlugin):

    def clean_bucket(self, message=None, quiet=True):
        try:
            from boto.s3.connection import S3Connection
            if (self.verify_setting_exists("WILL_AWS_ACCESS_KEY_ID", message=message) and 
                self.verify_setting_exists("WILL_AWS_SECRET_ACCESS_KEY", message=message) and
                self.verify_setting_exists("WILL_AWS_DEV_BUCKET_NAME", message=message)
               ):
                conn = S3Connection(settings.WILL_AWS_ACCESS_KEY_ID, settings.WILL_AWS_SECRET_ACCESS_KEY)
                try:
                    bucket = conn.get_bucket(settings.WILL_AWS_DEV_BUCKET_NAME)
                except:
                    self.say("Could not find the bucket '%s'" % settings.WILL_AWS_DEV_BUCKET_NAME, message=message)

                if bucket:
                    num_removed = 0
                    for key in bucket.list():
                        key.delete()
                        num_removed += 1

                if num_removed > 0 or quiet is False:
                    self.say("I just cleaned up the dev bucket on AWS. %s objects deleted." % num_removed, message=message)

        except ImportError:
            self.say("Boto library not installed. Can't clean the dev buckets.", message=message)
            

    @periodic(hour='1', minute='0')
    def clean_buckets_at_1_am(self):
        self.clean_bucket()

    @respond_to("(clear|clean ?up|empty) the dev bucket")
    def clean_buckets_reply(self, message):
        self.say("Sure thing. Gimme one minute.", message=message)
        self.clean_bucket(message=message, quiet=False)