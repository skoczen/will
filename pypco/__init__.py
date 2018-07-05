"""
A Pythonic Object-Oriented wrapper to the PCO API

pypco is an object-oriented Python wrapper for the PCO REST API meant to
simplify connecting to the PCO API from Python as much as possible. The
goal is to create a simple interface that abstracts away all HTTP calls.
Furthermore, pypco seeks to prevent the need to spend much time in the
pypco documentation; once you've go thte library's basics down, all of your
time should be spent directly in PCO API docs as the pypco library should
mirror them exactly.

usage:
    >>> import pypco
    >>> pco = pypco.PCO()
    >>> person = pco.people.get_single_result(ID=1)
    >>> person.first_name = "bob"
    >>> person.save()

pypco supports OAUTH (though you have to do some of the legwork) and
Personal Access Token authentication.
"""

# Ensure models are loaded
import pypco.models.people
import pypco.models.services
import pypco.models.check_ins
import pypco.models.giving
import pypco.models.resources
import pypco.models.webhooks

# Export the interface we present to clients

# The primary PCO interface object
from .pco import PCO

# Utility functions for OAUTH
from .utils import get_browser_redirect_url
from .utils import get_oauth_access_token
