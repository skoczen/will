import pytest

from will import settings
from will.acl import get_acl_members, is_acl_allowed, verify_acl

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
    """Maps a single  user to one or more teams """

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


@pytest.mark.parametrize("team", [TEAM1, TEAM2])
def test_get_acl_members(team, settings_acl):
    assert get_acl_members(team) == settings.ACL[team]


@pytest.mark.parametrize("user,acls", VALID_USER_AND_TEAMS)
def test_is_acl_allowed_returns_true(user, acls, settings_acl):
    assert is_acl_allowed(user, acls)


@pytest.mark.parametrize("user,acls", INVALID_USER_AND_TEAMS)
def test_is_acl_allowed_returns_false(user, acls, settings_acl):
    assert not is_acl_allowed(user, acls)


def test_verify_acl_is_disabled():
    """DISABLE_ACL is True, means no ACLs everyone can execute"""
    settings.DISABLE_ACL = True
    assert verify_acl("some_message", "some_acl")
