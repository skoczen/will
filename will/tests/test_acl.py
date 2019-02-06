import pytest
from will import settings
from will.abstractions import Message, Person
from will.acl import get_acl_members, is_acl_allowed, verify_acl

ACL = {
    'ENGINEERING_OPS': ['bob', 'Alice'],
    'engineering_devs': ['eve']
}

VALID_USERS_AND_GROUPS = [
    ('bob', {'ENGINEERING_OPS'}),
    ('Alice', {'ENGINEERING_OPS'}),
    ('eve', {'engineering_devs'}),
    ('bob', {'ENGINEERING_OPS', 'engineering_devs'}),
    ('Alice', {'ENGINEERING_OPS', 'engineering_devs'}),
    ('eve', {'ENGINEERING_OPS', 'engineering_devs'})
]

INVALID_USERS_AND_GROUPS = [
    ('bob', {'engineering_devs'}),
    ('Alice', {'engineering_devs'}),
    ('eve', {'ENGINEERING_OPS'}),
    ('juan', {'ENGINEERING_OPS', 'engineering_devs'}),
    ('pedro', {'ENGINEERING_OPS', 'engineering_devs'})
]


def get_ids_for_user_to_groups(groups):
    """Set IDs to be shown by pytest for different parametrizations"""

    return ["{}, {}".format(user, acls) for user, acls in groups]


# Need to map each user to one or more groups, these are the values that are used
# for the parametrized fixtures
VALID_USERS_AND_GROUPS_IDS = get_ids_for_user_to_groups(VALID_USERS_AND_GROUPS)
INVALID_USERS_AND_GROUPS_IDS = get_ids_for_user_to_groups(
    INVALID_USERS_AND_GROUPS)


@pytest.fixture()
def settings_acl():
    """Set settings.ACL values"""
    settings.ACL = ACL


@pytest.fixture()
def build_message_with_acls(person, message):
    def _build_message_with_acls(user_and_groups):
        user, groups = user_and_groups
        p = person({"handle": user})
        m = message({"sender": p, "data": message({})})

        return m, groups

    return _build_message_with_acls


@pytest.fixture(params=VALID_USERS_AND_GROUPS, ids=VALID_USERS_AND_GROUPS_IDS)
def allowed_message_with_acls(request, build_message_with_acls):
    return build_message_with_acls(request.param)


@pytest.fixture(params=INVALID_USERS_AND_GROUPS, ids=INVALID_USERS_AND_GROUPS_IDS)
def not_allowed_message_with_acls(request, build_message_with_acls):
    return build_message_with_acls(request.param)


@pytest.mark.parametrize("group", ACL.keys())
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


def test_verify_acl_no_backend_support(not_allowed_message_with_acls):
    settings.DISABLE_ACL = False
    message, acls = not_allowed_message_with_acls
    message.data.backend_supports_acl = False
    assert verify_acl(message, acls)
