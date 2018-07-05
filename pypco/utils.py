"""Miscellaneous utility functions for pypco."""

import urllib
import requests

def get_browser_redirect_url(client_id, redirect_uri, scopes):
    """Get the URL to which the user's browser should be redirected.

    This helps you perform step 1 of PCO OAUTH as described at:
    http://planningcenter.github.io/api-docs/#personal-access-token

    Note: Valid PCO OAUTH scopes are: check_ins, giving, people, resources, and services

    Args:
        client_id (str): The client id for your app.
        redirect_uri (str): The redirect URI, identical to what was used in step 1.
        scopes (list): A list of the scopes to which you will authenticate (see above).
    """

    url = "https://api.planningcenteronline.com/oauth/authorize?"

    for scope in scopes:
        if scope not in ['check_ins', 'giving', 'people', 'resources', 'services']:
            raise ValueError("\"{}\" is not a valid PCO OAUTH scope.".format(scope))

    params = [
        ('client_id', client_id),
        ('redirect_uri', redirect_uri),
        ('response_type', 'code'),
        ('scope', ' '.join(scopes))
    ]

    return "{}{}".format(url, urllib.parse.urlencode(params))

def get_oauth_access_token(client_id, client_secret, code, redirect_uri):
    """Get the access token for the client.

    This assumes you have already completed steps 1 and 2 as described at:
    http://planningcenter.github.io/api-docs/#personal-access-token

    Args:
        client_id (str): The client id for your app.
        client_secret (str): The client secret for your app.
        code (int): The code code returned by step one of your OAUTH sequence.
        redirect_uri (str): The redirect URI, identical to what was used in step 1.
    """

    response = requests.post(
        "https://api.planningcenteronline.com/oauth/token",
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': "authorization_code"
        }
    )

    return response
