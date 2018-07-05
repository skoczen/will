"""Utility classes for endpoints."""

class PCOAuthConfig:
    """Auth configuration for PCO.

        Attributes:
            application_id (str): The application ID for your application (PAT).
            secret (str): The secret for your application (PAT).
            token (str): The token for your application (OAUTH).
            auth_type (PCOAuthType): The authentiation type specified by this config object.
    """

    def __init__(self, application_id=None, secret=None, token=None):

        self.application_id = application_id
        self.secret = secret
        self.token = token

    @property
    def auth_type(self):
        """The authentication type specified by this configuration.

        Raises:
            PCOAuthException: You have specified invalid authentication information.
        """

        if self.application_id and self.secret and not self.token:
            return PCOAuthType.PAT
        elif self.token and not (self.application_id or self.secret):
            return PCOAuthType.OAUTH
        else:
            raise PCOAuthException(
                "You have specified invalid authentication information."
                "You must specify either an application id and a secret for"
                "your Personal Access Token (PAT) or an OAuth token."
            )

class PCOAuthType: #pylint: disable=R0903
    """Defines PCO authentication types."""

    PAT = 0
    OAUTH = 1

class PCOAuthException(Exception):
    """Defines an exception thrown when initializating a PCO object."""

    pass
