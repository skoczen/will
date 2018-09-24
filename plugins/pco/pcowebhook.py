from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from plugins.pco import birthday, address, phone_numbers, checkins, msg_attachment, authenticate, pcoservices
import logging
import json


class PcoWebhook(WillPlugin):
    """pcowebhook is for catching and dealing with Planning Center Webhooks"""

    @route("/pco/webhook", method='POST')
    def pco_webhook_endpoint(self):
        logging.info("Recieved Webhook from PCO!")
        data = self.request.json
        self.parse_pco_webhook(data)
        return "Successfully recieved webhook!"

    def parse_pco_webhook(self, data):
        """Parsing should be done here and passed to other methods to deal with the event."""
        logging.info("Parsing PCO Webhook")
        data = data['data'][0]
        endpoint = data['attributes']['name']
        logging.info("Webhook is %s" % endpoint)
        payload = json.loads(data['attributes']['payload'])
        payload = payload['data']
        logging.info("Payload is type: %s" % type(payload))
        if endpoint == 'people.v2.events.person.updated':
            # logging.info(("Person ID: %s" % payload['id']))
            # logging.info(payload['attributes']['name'])
            pass
        elif endpoint == 'people.v2.events.person.created':
            self.person_created(payload)

    def person_created(self, data):
        logging.info('Pco Person Created Webhook Triggered')
        pcoaddress = "https://people.planningcenteronline.com/people/" + data['id']
        attachment = msg_attachment.SlackAttachment("Lets all welcome %s!" % data['attributes']['name'],
                                                    text="New Person added to Planning Center!\nLets all welcome %s!" %
                                                         data['attributes']['name'],
                                                    button_text="Open in People",
                                                    button_url=pcoaddress)
        logging.info(attachment.slack())
        self.say("", channel=self.announcement_channel(), attachments=attachment.slack())

    def announcement_channel(self):
        """Used for retrieving the current announcement channel"""
        if self.load('announcement_channel'):
            channel = self.load('announcement_channel')
        else:
            self.save('announcement_channel', 'announcements')
            channel = 'announcements'
        return channel

