from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings

from datetime import datetime, timedelta
import pypd


class PagerDutyPlugin(WillPlugin):

    def __init__(self):
        if getattr(settings, 'PAGERDUTY_APIV2_KEY', False):
            pypd.api_key = settings.PAGERDUTY_APIV2_KEY

    def get_email_from_hipchat_id(self, hipchat_id):
        return self.get_hipchat_user(hipchat_id)['email']

    def get_hipchat_id_from_nick(self, nick):
        user = self.get_user_by_nick(nick.lstrip('@'))
        if user:
            return user['hipchat_id']

        return None

    @staticmethod
    def get_pagerduty_user(email_address):
        return pypd.User.find_one(email=email_address)

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd list$')
    def list_own(self, message):
        """List all ongoing incidents assigned to you."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged'], user_ids=[pd_user['id']]):
            creation_datetime = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            incidents.append({
                'status': incident['status'],
                'html_url': incident['html_url'],
                'summary': incident['summary'],
                'assignees': ', '.join([
                    assignment['assignee']['summary']
                    for assignment in incident['assignments']
                ]),
                'created_at': self.to_natural_day_and_time(creation_datetime, with_timezone=True),
            })

        if incidents:
            self.say(
                rendered_template('pagerduty_incidents.html', {'incidents': incidents}),
                message=message,
                html=True,
            )
        else:
            self.reply('No ongoing incidents found assigned to you')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd list!$')
    def list_all(self, message):
        """List all ongoing incidents."""
        incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged']):
            creation_datetime = datetime.strptime(incident['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            incidents.append({
                'status': incident['status'],
                'html_url': incident['html_url'],
                'summary': incident['summary'],
                'assignees': ', '.join([
                    assignment['assignee']['summary']
                    for assignment in incident['assignments']
                ]),
                'created_at': self.to_natural_day_and_time(creation_datetime, with_timezone=True),
            })

        if incidents:
            self.say(
                rendered_template('pagerduty_incidents.html', {'incidents': incidents}),
                message=message,
                html=True,
            )
        else:
            self.reply('No ongoing incidents found')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd ack$')
    def acknowledge_own(self, message):
        """Acknowledge ongoing incidents assigned to you."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        acknowledged_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered'], user_ids=[pd_user['id']]):
            incident.acknowledge(pd_user['email'])
            acknowledged_incidents.append(str(incident['incident_number']))

        if acknowledged_incidents:
            self.reply('Acknowledged {} incidents: {}'.format(len(acknowledged_incidents), ', '.join(acknowledged_incidents)))
        else:
            self.reply('No triggered incidents found assigned to you')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd ack (?P<incidents>[\w ]+)$')
    def acknowledge_some(self, message, incidents):
        """Acknowledge specific incidents."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        incident_ids = incidents.split(' ')
        acknowledged_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered']):
            if str(incident['incident_number']) not in incident_ids and incident['id'] not in incident_ids:
                continue

            incident.acknowledge(pd_user['email'])
            acknowledged_incidents.append(str(incident['incident_number']))

        if acknowledged_incidents:
            self.reply('Acknowledged {} incidents: {}'.format(len(acknowledged_incidents), ', '.join(acknowledged_incidents)))
        else:
            self.reply('No triggered incidents found with the provided IDs')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd ack!$')
    def acknowledge_all(self, message):
        """Acknowledge all ongoing incidents."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        acknowledged_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered']):
            incident.acknowledge(pd_user['email'])
            acknowledged_incidents.append(str(incident['incident_number']))

        if acknowledged_incidents:
            self.reply('Acknowledged {} incidents: {}'.format(len(acknowledged_incidents), ', '.join(acknowledged_incidents)))
        else:
            self.reply('No triggered incidents found')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd resolve$')
    def resolve_own(self, message):
        """Resolve ongoing incidents assigned to you."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        resolved_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged'], user_ids=[pd_user['id']]):
            incident.resolve(pd_user['email'])
            resolved_incidents.append(str(incident['incident_number']))

        if resolved_incidents:
            self.reply('Resolved {} incidents: {}'.format(len(resolved_incidents), ', '.join(resolved_incidents)))
        else:
            self.reply('No ongoing incidents found assigned to you')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd resolve (?P<incidents>[\w ]+)$')
    def resolve_some(self, message, incidents):
        """Resolve specific incidents."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        incident_ids = incidents.split(' ')
        resolved_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged']):
            if str(incident['incident_number']) not in incident_ids and incident['id'] not in incident_ids:
                continue

            incident.resolve(pd_user['email'])
            resolved_incidents.append(str(incident['incident_number']))

        if resolved_incidents:
            self.reply('Resolved {} incidents: {}'.format(len(resolved_incidents), ', '.join(resolved_incidents)))
        else:
            self.reply('No ongoing incidents found with the provided IDs')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd resolve!$')
    def resolve_all(self, message):
        """Resolve all ongoing incidents."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        resolved_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged'], user_ids=[pd_user['id']]):
            incident.resolve(pd_user['email'])
            resolved_incidents.append(str(incident['incident_number']))

        if resolved_incidents:
            self.reply('Resolved {} incidents: {}'.format(len(resolved_incidents), ', '.join(resolved_incidents)))
        else:
            self.reply('No ongoing incidents found')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd reassign (?P<incidents>[\w ]+) (?P<receiver>[a-zA-Z0-9@]+)$')
    def reassign(self, message, incidents, receiver):
        """Assign incidents to another person."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        receiver_id = self.get_hipchat_id_from_nick(receiver)
        if not receiver_id:
            return self.reply('I could not find a HipChat user based on "{}"'.format(receiver), color='yellow')

        receiver_email = self.get_email_from_hipchat_id(receiver_id)
        receiver_pd_user = self.get_pagerduty_user(receiver_email)
        if not receiver_pd_user:
            return self.reply(
                'I could not find a PagerDuty user based on the mail address: {}'.format(receiver_email),
                color='yellow',
            )

        incident_ids = incidents.split(' ')
        reassigned_incidents = []
        for incident in pypd.Incident.find(statuses=['triggered', 'acknowledged']):
            if str(incident['incident_number']) not in incident_ids and incident['id'] not in incident_ids:
                continue

            incident.reassign(pd_user['email'], [receiver_pd_user['id']])

            if pd_user['email'] == receiver_pd_user['email']:
                # PagerDuty unacknowledges an incident when it's reassigned, so lets
                # acknowledge it if we are assigning to the person who requested it.
                incident.acknowledge(pd_user['email'])

            reassigned_incidents.append(str(incident['incident_number']))

        if reassigned_incidents:
            self.reply('Reassigned {} incidents: {}'.format(len(reassigned_incidents), ', '.join(reassigned_incidents)))
        else:
            self.reply('No ongoing incidents found with the provided IDs')

    @require_settings('PAGERDUTY_APIV2_KEY')
    @respond_to(r'^pd maintenance (?P<service>.+) (?P<interval>[0-9]+[hdw])$')
    def maintenance(self, message, service, interval):
        """Create a maintenance window for a service."""
        sender_email = self.get_email_from_hipchat_id(message.sender['hipchat_id'])
        pd_user = self.get_pagerduty_user(sender_email)
        if not pd_user:
            return self.reply(
                'I cannot find your PagerDuty user based on your HipChat mail address: {}'.format(sender_email),
                color='yellow',
            )

        service_name = service.strip().lower()

        interval_value, interval_unit = int(interval[:-1]), interval[-1]
        if not interval_value:
            return self.reply('The time period specified equals to nothing', color='yellow')

        if interval_unit == 'h':
            interval = timedelta(hours=interval_value)
        elif interval_unit == 'd':
            interval = timedelta(days=interval_value)
        elif interval_unit == 'w':
            interval = timedelta(weeks=interval_value)

        for i in pypd.Service.find(query=service_name):
            if i['name'].lower() != service_name:
                continue

            service = i
            break
        else:
            return self.reply(
                'I cannot find a service with the name "{}" in PagerDuty'.format(service.strip()),
                color='yellow',
            )

        pypd.MaintenanceWindow.create(
            add_headers={'from': pd_user['email']},
            data={
                'start_time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S-00:00'),
                'end_time': (datetime.utcnow() + interval).strftime('%Y-%m-%dT%H:%M:%S-00:00'),
                'services': [{
                    'id': service['id'],
                    'type': 'service_reference',
                }],
            },
        )

        self.reply(
            'Maintenance window for "{}" has been created lasting until {}'.format(
                service['name'],
                self.to_natural_day_and_time(datetime.now() + interval, with_timezone=True),
            ),
        )
