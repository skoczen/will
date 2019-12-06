import requests

from will import settings


class SmsMixin(object):

    def send_sms(self, from_number=None, recipient=None, message=""):
        if not hasattr(settings, 'TWILIO_ACCOUNT_SID'):
            raise Exception("Will requires a Twilio account sid in the environment variable TWILIO_ACCOUNT_SID")

        if not hasattr(settings, 'TWILIO_AUTH_TOKEN'):
            raise Exception("Will requires a Twilio auth token in the environment variable TWILIO_AUTH_TOKEN")

        if from_number is None:
            if hasattr(settings, 'DEFAULT_FROM_NUMBER'):
                from_number = settings.DEFAULT_FROM_NUMBER
            else:
                raise ValueError("Couldn't send sms, from_number was None and there was no DEFAULT_FROM_NUMBER")

        if not recipient:
            raise ValueError("Recipient wasn't specified. Expecting a number, got %s" % recipient)

        api_version = getattr(settings, 'TWILIO_API_VERSION', None)
        if api_version is None:
            raise ValueError("TWILIO_API_VERSION is None, it is required")

        resp = requests.post(
            "https://api.twilio.com/%s/Accounts/%s/Messages" % (api_version, settings.TWILIO_ACCOUNT_SID),
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            data={
                "From": from_number,
                "To": recipient,
                "Body": message,
            }
        )

        if resp.status_code != 201:
            raise Exception("Could not send sms, got a %s response posting to twilio. %s" % resp.status_code)
