import pytest

from will import settings
from will.abstractions import Message, Person
from will.acl import get_acl_members, is_acl_allowed, verify_acl

USERS_GROUP1 = ["bob", "Alice"]
USERS_GROUP2 = ["eve"]
USERS_NO_GROUP = ["juan", "pedro"]

GROUP1 = "ENGINEERING_OPS"
GROUP2 = "engineering_devs"

ACL = {
    GROUP1: USERS_GROUP1,
    GROUP2: USERS_GROUP2
}

# Plugins are assigned to one or more ACLs, that's why valid group and invalid group have
# to have a test with one or more groups
VALID_GROUP = [(USERS_GROUP1, {GROUP1}),
               (USERS_GROUP2, {GROUP2}),
               (USERS_GROUP1 + USERS_GROUP2, {GROUP1, GROUP2})]

INVALID_GROUP = [(USERS_GROUP1, {GROUP2}),
                 (USERS_GROUP2, {GROUP1}),
                 (USERS_NO_GROUP, {GROUP1, GROUP2})]


def map_user_to_groups(groups):
    """Maps a single user to one or more groups """

    return [(user, groups) for users, groups in groups for user in users]

def get_ids_for_user_to_groups(groups):
    """Set IDs to be shown by pytest for different parametrizations"""
    return ["{}, {}".format(user, acls) for user, acls in groups]

# Need to map each user to one or more groups, these are the values that are used
# for the parametrized fixtures
VALID_USERS_AND_GROUPS = map_user_to_groups(VALID_GROUP)
INVALID_USERS_AND_GROUPS = map_user_to_groups(INVALID_GROUP)
VALID_USERS_AND_GROUPS_IDS = get_ids_for_user_to_groups(VALID_USERS_AND_GROUPS)
INVALID_USERS_AND_GROUPS_IDS = get_ids_for_user_to_groups(INVALID_USERS_AND_GROUPS)


@pytest.fixture()
def settings_acl():
    """Set settings.ACL values"""
    settings.ACL = ACL

    yield


@pytest.fixture()
def build_message_with_acls(person, message):
    def _build_message_with_acls(user_and_groups):
        user, groups = user_and_groups
        p = person({"handle": user})
        m = message({"sender": p})

        return m, groups
    return _build_message_with_acls


@pytest.fixture(params=VALID_USERS_AND_GROUPS, ids=VALID_USERS_AND_GROUPS_IDS)
def allowed_message_with_acls(request, build_message_with_acls):
    return build_message_with_acls(request.param)


@pytest.fixture(params=INVALID_USERS_AND_GROUPS, ids=INVALID_USERS_AND_GROUPS_IDS)
def not_allowed_message_with_acls(request, build_message_with_acls):
    return build_message_with_acls(request.param)


@pytest.mark.parametrize("group", [GROUP1, GROUP2])
def test_get_acl_members(group, settings_acl):
    assert get_acl_members(group) == settings.ACL[group]


def test_is_acl_allowed_returns_true(allowed_message_with_acls):
    message, acls = allowed_message_with_acls
    assert is_acl_allowed(message.sender.handle, acls)


def test_is_acl_allowed_returns_false(not_allowed_message_with_acls):
    message, acls = not_allowed_message_with_acls
    assert not is_acl_allowed(message.sender.handle, acls)


def test_verify_acl_is_disabled(not_allowed_message_with_acls):
    """DISABLE_ACL True, means everyone can execute, so not allowed messages are allowed"""
    settings.DISABLE_ACL = True
    message, acls = not_allowed_message_with_acls
    assert verify_acl(message, acls)


def test_verify_acl_is_allowed(allowed_message_with_acls):
    settings.DISABLE_ACL = False
    message, acls = allowed_message_with_acls
    assert verify_acl(message, acls)


def test_verify_acl_is_not_allowed(not_allowed_message_with_acls):
    settings.DISABLE_ACL = False
    message, acls = not_allowed_message_with_acls
    assert not verify_acl(message, acls)
