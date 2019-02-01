import pytest

from will import settings
from will.acl import is_acl_allowed

USERS_TEAM1 = ["bob", "Alice"]
USERS_TEAM2 = ["eve"]
USERS_NO_GROUP = ["juan", "pedro"]

TEAM1 = "ENGINEERING_OPS"
TEAM2 = "engineering_devs"

VALID_GROUP = ((USERS_TEAM1, {TEAM1}),
               (USERS_TEAM2, {TEAM2}),
               (USERS_TEAM1 + USERS_TEAM2, {TEAM1, TEAM2}))

INVALID_GROUP = ((USERS_TEAM1, {TEAM2}),
                 (USERS_TEAM2, {TEAM1}),
                 (USERS_NO_GROUP, {TEAM1, TEAM2}))


def map_user_to_teams(groups):
    return [(user, teams) for users, teams in groups for user in users]


VALID_USER_AND_TEAMS = map_user_to_teams(VALID_GROUP)
INVALID_USER_AND_TEAMS = map_user_to_teams(INVALID_GROUP)


@pytest.fixture()
def settings_acl():
    """Set settings.ACL values"""
    acl = {
        TEAM1: USERS_TEAM1,
        TEAM2: USERS_TEAM2
    }
    settings.ACL = acl
    yield


@pytest.mark.parametrize("users_and_acls", VALID_USER_AND_TEAMS)
def test_is_acl_allowed_returns_true(users_and_acls, settings_acl):
    assert is_acl_allowed(*users_and_acls)


@pytest.mark.parametrize("users_and_acls", INVALID_USER_AND_TEAMS)
def test_is_acl_allowed_returns_false(users_and_acls, settings_acl):
    assert not is_acl_allowed(*users_and_acls)
