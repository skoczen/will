import pytest

from will.abstractions import Message, Person

# Any fixtures defined in this file will be automatically imported into
# discovered tests.
# https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions


@pytest.fixture()
def person():
    """Mimic person abstraction"""
    def _person(fields):
        required_fields = {
            "id": "TDB",
            "mention_handle": "TBD",
            "source": "TBD",
            "handle": "TBD",
            "name": "TBD",
            "first_name": "TDB"
        }
        required_fields.update(fields)

        return Person(**required_fields)

    return _person


@pytest.fixture()
def message():
    """Mimic message abstraction"""
    def _message(fields):
        required_fields = {
            "is_direct": False,
            "is_private_chat": False,
            "is_group_chat": True,
            "will_is_mentioned": False,
            "will_said_it": False,
            "sender": "TBD",
            "backend_supports_acl": True,
            "content": "TBD",
            "backend": "TBD",
            "original_incoming_event": "TBD"
        }
        required_fields.update(fields)

        return Message(**required_fields)
    return _message
