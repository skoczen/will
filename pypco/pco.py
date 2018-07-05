"""Module containing the main PCO object for the PCO API wrapper."""

import logging
from .endpoints import PCOAuthConfig, BaseEndpoint

class PCO(object):
    """The entry point to the PCO API.

    Attributes:
        auth_config (PCOAuthConfig): The authentication configuration for this instance.
    """

    def __init__(self, application_id=None, secret=None, token=None):
        """Initialize the PCO entry point.

        Note:
            You must specify either an application ID and a secret or an oauth token.
            If you specify an invalid combination of these arguments, an exception will be
            raised when you attempt to make API calls.
        """

        self._log = logging.getLogger(__name__)
        self._log.info("Initializing the PCO wrapper.")

        self.auth_config = PCOAuthConfig(application_id, secret, token)
        self._log.debug("Initialized the auth_config object.")

        for klass in BaseEndpoint.__subclasses__():
            setattr(self, klass.resolve_root_endpoint_name(), klass(self.auth_config, self))
       
    def new(self, klass):
        """Return a new instance of a PCO object that should be modified and pushed to the API.

        Note: This factory function is the only supported way to create new objects in the PCO
        API. You should not be creating new instances of the model classes directly.

        Args:
            klass (class): The class representing the new object to be created in the PCO API.

        Returns:
            Returns an initialized model object as specified by the klass argument. This new object
            is ready to be modified and saved to the API using the model's create function.

        Example:
            >>> import pypco
            >>> pco = pypco.PCO('<app_id>', '<app_secret>')
            >>> # New takes the model class as an argument.
            >>> # Model classes are resolved like: pypco.models.<endpoint>.<model>
            >>> new_guy = pco.new(pypco.models.people.Person)
            >>> new_guy.first_name = "Pico"
            >>> new_guy.last_name = "Robot"
            >>> new_guy.create()
        """

        base_endpoint = getattr(self, klass.__module__.split('.')[-1])
        endpoint = getattr(base_endpoint, klass.ENDPOINT_NAME)

        data = {
            'type': klass.__name__,
            'attributes': {}
        }

        return klass(endpoint, data, user_created=True)
