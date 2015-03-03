import base64
import ssl
import logging

from sleekxmpp.util import bytes, sasl
from sleekxmpp.util.stringprep_profiles import StringPrepError
from sleekxmpp.stanza import StreamFeatures
from sleekxmpp.xmlstream import StanzaBase, RestartStream, register_stanza_plugin
from sleekxmpp.plugins import BasePlugin
from sleekxmpp.xmlstream.matcher import MatchXPath
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.features.feature_mechanisms import stanza
import settings

log = logging.getLogger(__name__)


class CustomAuth(stanza.Auth):
    """
    """

    name = 'auth'
    # namespace = 'urn:ietf:params:xml:ns:xmpp-sasl'
    namespace = 'http://hipchat.com'
    interfaces = set(('mechanism', 'value'))
    plugin_attrib = name

    #: Some SASL mechs require sending values as is,
    #: without converting base64.
    plain_mechs = set(['X-MESSENGER-OAUTH2'])

    def setup(self, xml):
        StanzaBase.setup(self, xml)
        self.xml.tag = self.tag_name()
        self.xml.set("oauth2_token", "true")

    def get_value(self):
        if not self['mechanism'] in self.plain_mechs:
            return base64.b64decode(bytes(self.xml.text))
        else:
            return self.xml.text

    def set_value(self, values):
        if not self['mechanism'] in self.plain_mechs:
            values = "0%s0%s0will" % (
                settings.USERNAME,  # Tried 1234456_784560@chat.hipchat.com or will_email@example.com
                settings.PASSWORD,  # password
            )
            if values:
                self.xml.text = bytes(base64.b64encode(values)).decode('utf-8')
            elif values == b'':
                self.xml.text = '='
        else:
            self.xml.text = bytes(values).decode('utf-8')

    def del_value(self):
        self.xml.text = ''


class HipChatAuth(BasePlugin):

    name = 'hipchat_auth'
    description = 'HipChat Authentication'
    dependencies = set()
    stanza = stanza
    default_config = {
        'use_mech': None,
        'use_mechs': None,
        'min_mech': None,
        'sasl_callback': None,
        'security_callback': None,
        'encrypted_plain': True,
        'unencrypted_plain': False,
        'unencrypted_digest': False,
        'unencrypted_cram': False,
        'unencrypted_scram': True,
        'order': 100
    }

    def plugin_init(self):
        if self.sasl_callback is None:
            self.sasl_callback = self._default_credentials

        if self.security_callback is None:
            self.security_callback = self._default_security

        creds = self.sasl_callback(set(['username']), set())
        if not self.use_mech and not creds['username']:
            self.use_mech = 'ANONYMOUS'

        self.mech = None
        self.mech_list = set()
        self.attempted_mechs = set()

        register_stanza_plugin(StreamFeatures, stanza.Mechanisms)

        self.xmpp.register_stanza(stanza.Success)
        self.xmpp.register_stanza(stanza.Failure)
        self.xmpp.register_stanza(CustomAuth)
        self.xmpp.register_stanza(stanza.Challenge)
        self.xmpp.register_stanza(stanza.Response)
        self.xmpp.register_stanza(stanza.Abort)

        self.xmpp.register_handler(
            Callback(
                'SASL Success',
                MatchXPath(stanza.Success.tag_name()),
                self._handle_success,
                instream=True)
        )
        self.xmpp.register_handler(
            Callback(
                'SASL Failure',
                MatchXPath(stanza.Failure.tag_name()),
                self._handle_fail,
                instream=True)
        )
        self.xmpp.register_handler(
            Callback(
                'SASL Challenge',
                MatchXPath(stanza.Challenge.tag_name()),
                self._handle_challenge)
        )
        self.xmpp.register_feature(
            'mechanisms',
            self._handle_sasl_auth,
            restart=True,
            order=self.order
        )

    def _default_credentials(self, required_values, optional_values):
        creds = self.xmpp.credentials
        result = {}
        values = required_values.union(optional_values)
        for value in values:
            if value == 'username':
                result[value] = creds.get('username', self.xmpp.requested_jid.user)
            elif value == 'email':
                jid = self.xmpp.requested_jid.bare
                result[value] = creds.get('email', jid)
            elif value == 'channel_binding':
                if hasattr(self.xmpp.socket, 'get_channel_binding'):
                    result[value] = self.xmpp.socket.get_channel_binding()
                else:
                    log.debug("Channel binding not supported.")
                    log.debug("Use Python 3.3+ for channel binding and "
                              "SCRAM-SHA-1-PLUS support")
                    result[value] = None
            elif value == 'host':
                result[value] = creds.get('host', self.xmpp.requested_jid.domain)
            elif value == 'realm':
                result[value] = creds.get('realm', self.xmpp.requested_jid.domain)
            elif value == 'service-name':
                result[value] = creds.get('service-name', self.xmpp._service_name)
            elif value == 'service':
                result[value] = creds.get('service', 'xmpp')
            elif value in creds:
                result[value] = creds[value]
        return result

    def _default_security(self, values):
        result = {}
        for value in values:
            if value == 'encrypted':
                if 'starttls' in self.xmpp.features:
                    result[value] = True
                elif isinstance(self.xmpp.socket, ssl.SSLSocket):
                    result[value] = True
                else:
                    result[value] = False
            else:
                result[value] = self.config.get(value, False)
        return result

    def _handle_sasl_auth(self, features):
        """
        Handle authenticating using SASL.
        Arguments:
            features -- The stream features stanza.
        """
        if 'mechanisms' in self.xmpp.features:
            # SASL authentication has already succeeded, but the
            # server has incorrectly offered it again.
            return False

        enforce_limit = False
        limited_mechs = self.use_mechs

        if limited_mechs is None:
            limited_mechs = set()
        elif limited_mechs and not isinstance(limited_mechs, set):
            limited_mechs = set(limited_mechs)
            enforce_limit = True

        if self.use_mech:
            limited_mechs.add(self.use_mech)
            enforce_limit = True

        if enforce_limit:
            self.use_mechs = limited_mechs

        self.mech_list = set(features['mechanisms'])

        return self._send_auth()

    def _send_auth(self):
        print self.mech_list
        mech_list = self.mech_list - self.attempted_mechs
        try:
            self.mech = sasl.choose(mech_list,
                                    self.sasl_callback,
                                    self.security_callback,
                                    limit=self.use_mechs,
                                    min_mech=self.min_mech)
        except sasl.SASLNoAppropriateMechanism:
            log.error("No appropriate login method.")
            self.xmpp.event("no_auth", direct=True)
            self.xmpp.event("failed_auth", direct=True)
            self.attempted_mechs = set()
            return self.xmpp.disconnect()
        except StringPrepError:
            log.exception("A credential value did not pass SASLprep.")
            self.xmpp.disconnect()

        print "stanza"
        print CustomAuth
        print self.xmpp
        resp = CustomAuth(self.xmpp)
        resp['mechanism'] = self.mech.name
        try:
            resp['value'] = self.mech.process()
        except sasl.SASLCancelled:
            self.attempted_mechs.add(self.mech.name)
            self._send_auth()
        except sasl.SASLFailed:
            self.attempted_mechs.add(self.mech.name)
            self._send_auth()
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! "
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        else:
            resp.send(now=True)

        return True

    def _handle_challenge(self, stanza):
        """SASL challenge received. Process and send response."""
        resp = self.stanza.Response(self.xmpp)
        try:
            resp['value'] = self.mech.process(stanza['value'])
        except sasl.SASLCancelled:
            self.stanza.Abort(self.xmpp).send()
        except sasl.SASLFailed:
            self.stanza.Abort(self.xmpp).send()
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! "
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        else:
            if resp.get_value() == '':
                resp.del_value()
            resp.send(now=True)

    def _handle_success(self, stanza):
        """SASL authentication succeeded. Restart the stream."""
        try:
            self.mech.process(stanza['value'])
        except sasl.SASLMutualAuthFailed:
            log.error("Mutual authentication failed! "
                      "A security breach is possible.")
            self.attempted_mechs.add(self.mech.name)
            self.xmpp.disconnect()
        else:
            self.attempted_mechs = set()
            self.xmpp.authenticated = True
            self.xmpp.features.add('mechanisms')
            self.xmpp.event('auth_success', stanza, direct=True)
            raise RestartStream()

    def _handle_fail(self, stanza):
        """SASL authentication failed. Disconnect and shutdown."""
        self.attempted_mechs.add(self.mech.name)
        log.info("Authentication failed: %s", stanza['condition'])
        self.xmpp.event("failed_auth", stanza, direct=True)
        self._send_auth()
        return True
