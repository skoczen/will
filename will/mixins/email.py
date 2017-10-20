import requests

from will import settings


class EmailMixin(object):

    def send_email(self, from_email=None, email_list=[], subject="", message=""):
        if not hasattr(settings, 'MAILGUN_API_KEY'):
            raise Exception("Will requires a Mailgun api key in the environment variable MAILGUN_API_KEY")

        if from_email is None:
            if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
                from_email = settings.DEFAULT_FROM_EMAIL
            else:
                raise ValueError("Couldn't send email, from_email was None and there was no DEFAULT_FROM_EMAIL")

        if not email_list:
            raise ValueError("Email list wasn't specified. Expecting a list of emails, got %s" % email_list)

        api_url = getattr(settings, 'MAILGUN_API_URL', None)
        if api_url is None:
            raise ValueError("MAILGUN_API_URL is None, it is required")

        resp = requests.post(
            "https://api.mailgun.net/v2/%s/messages" % api_url,
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": from_email,
                "to": email_list,
                "subject": subject,
                "text": message,
            }
        )

        if resp.status_code != 200:
            raise Exception("Could not send email, got a %s response posting to mailgun" % resp.status_code)
