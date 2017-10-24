from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings

import datetime
import pygerduty


class PagerDutyPlugin(WillPlugin):

    @staticmethod
    def _associate_pd_user(email_address, pager):
        try:
            user = next(pager.users.list(query=email_address, limit=1))
            return user
        except StopIteration:
            return None

    def _get_user_email_from_mention_name(self, mention_name):
        try:
            u = self.get_user_by_nick(mention_name[1:])
            email_address = self.get_user(u['hipchat_id'])['email']
            return email_address
        except TypeError:
            return None

    def _update_incident(self, message, incidents, action, assign_to_email=None):
        pager = pygerduty.PagerDuty(settings.PAGERDUTY_SUBDOMAIN, settings.PAGERDUTY_API_KEY)
        email_address = self.get_user(message.sender['hipchat_id'])['email']
        user = self._associate_pd_user(email_address, pager)
        if user is None:
            self.reply("I couldn't find your user :(")
            return

        # if incident(s) are given
        if incidents:
            for i in incidents:
                # for specific incident, use show
                try:
                    incident = pager.incidents.show(entity_id=i)
                except pygerduty.BadRequest as e:
                    if e.code == 5001:
                        self.reply("Incident %s was not found." % i, color="yellow")
                    continue
                if action == 'ack':
                    try:
                        incident.acknowledge(requester_id=user.id)
                    except pygerduty.BadRequest as e:
                        if e.code == 1001:
                            self.reply("%s has been already resolved." % i, color="yellow")
                        continue
                elif action == 'resolve':
                    try:
                        incident.resolve(requester_id=user.id)
                    except pygerduty.BadRequest as e:
                        if e.code == 1001:
                            self.reply("%s has been already resolved." % i, color="yellow")
                        continue
                elif action == 'reassign':
                    try:
                        if assign_to_email is not None:
                            assign_to = self._associate_pd_user(assign_to_email, pager)
                            if assign_to is None:
                                self.reply("Coudn't find the PD user for %s :(" % assign_to_email)
                                return
                            else:
                                incident.reassign(user_ids=[assign_to.id], requester_id=user.id)
                    except pygerduty.BadRequest:
                        # ignore any error, maybe it worth to log it somewhere
                        # in the future
                        continue
            self.reply("Ok.")
        # if incident(s) are not given
        else:
            try:
                # acknowledge assigned incidents
                if action == 'ack':
                    for incident in pager.incidents.list(status='triggered', assigned_to=user):
                        incident.acknowledge(requester_id=user.id)
                # acknowledge all incidets
                elif action == 'ack_all':
                    for incident in pager.incidents.list(status='triggered'):
                        incident.acknowledge(requester_id=user.id)
                # resolve assigned incidents
                elif action == 'resolve':
                    for incident in pager.incidents.list(status='acknowledged', assigned_to=user):
                        incident.resolve(requester_id=user.id)
                # resolve all incidents
                elif action == 'resolve_all':
                    for incident in pager.incidents.list(status='acknowledged'):
                        incident.resolve(requester_id=user.id)
                self.reply("Ok.")
            except pygerduty.BadRequest:
                # ignore any error, might be acked/resolved
                pass

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd ack$")
    def ack_all_assigned_incidents(self, message):
        self._update_incident(message, None, 'ack')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd ack (?P<incidents>[0-9 ]*)")
    def ack_incidents(self, message, incidents):
        self._update_incident(message, incidents.split(" "), 'ack')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd ack!$")
    def ack_all_incidents(self, message):
        self._update_incident(message, None, 'ack_all')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd resolve$")
    def resolve_all_assigned_and_acknowledged_incidents(self, message):
        self._update_incident(message, None, 'resolve')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd resolve (?P<incidents>[0-9 ]*)")
    def resolve_incidens(self, message, incidents):
        self._update_incident(message, incidents.split(" "), 'resolve')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd resolve!$")
    def resolve_all_incidents(self, message):
        self._update_incident(message, None, 'resolve_all')

    @require_settings("PAGERDUTY_SUBDOMAIN", "PAGERDUTY_API_KEY")
    @respond_to("^pd maintenance (?P<service_name>[\S+ ]+) (?P<interval>[1-9])h$")
    def set_service_maintenance(self, message, service_name=None, interval=None):
        if not interval:
            interval = 1
        pager = pygerduty.PagerDuty(settings.PAGERDUTY_SUBDOMAIN, settings.PAGERDUTY_API_KEY)
        for service in pager.services.list(limit=50):
            if service.name == service_name:
                user = self._associate_pd_user(self.get_user(message.sender['hipchat_id'])['email'], pager)
                if user is None:
                    self.reply("I couldn't find your user :(", color="yellow")
                    return
                now = datetime.datetime.utcnow()
                start_time = now.strftime("%Y-%m-%dT%H:%MZ")
                end_time = (now + datetime.timedelta(hours=int(interval))).strftime("%Y-%m-%dT%H:%MZ")
                try:
                    pager.maintenance_windows.create(service_ids=[service.id], requester_id=user.id,
                                                     start_time=start_time,
                                                     end_time=end_time)
                    self.reply("Ok.")
                except pygerduty.BadRequest as e:
                    self.reply("Failed: %s" % e.message, color="yellow")

    @respond_to("^pd reassign (?P<incidents>[0-9 ]+)( )(?P<mention_name>[a-zA-Z@]+)$")
    def reassign_incidents(self, message, incidents, mention_name):
        email_address = self._get_user_email_from_mention_name(mention_name)
        if email_address:
            self._update_incident(message, incidents.split(" "), 'reassign', email_address)
        else:
            self.reply("Can't find email address for %s" % mention_name)
