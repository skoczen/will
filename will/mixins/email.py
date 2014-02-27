import requests

import settings


class EmailMixin(object):

    def send_email(self, from_email=None, email_list=[], subject="", message=""):
        if not hasattr(settings, 'WILL_MAILGUN_API_KEY'):
            raise Exception("Will requires a Mailgun api key in the environment variable WILL_MAILGUN_API_KEY")

        if from_email is None:
            from_email = settings.WILL_DEFAULT_FROM_EMAIL

            if from_email is None:
                raise ValueError("Couldn't send email, from_email was None and there was no WILL_DEFAULT_FROM_EMAIL")

        if email_list is None or len(email_list) == 0:
            raise ValueError("Couldn't send email, email_list was None or empty?!")

        resp = requests.post(
            "https://api.mailgun.net/v2/scrapbin.com/messages",
            auth=("api", settings.WILL_MAILGUN_API_KEY),
            data={
                "from": from_email,
                "to": email_list,
                "subject": "Website 500 error",
                "text": message
            }
        )

        if resp.status_code != 200:
            raise Exception("Could not send email, got a %s response" % resp.status_code)
