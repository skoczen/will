import unittest

from will.mixins.roster import RosterMixin
from will import settings
from will.acl import get_acl_settings_name, get_acl_members, is_acl_allowed
from mock import patch


class TestIsAdmin(unittest.TestCase):

    def setUp(self):
        self.message = {'nick': 'WoOh'}

    @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    def test_message_is_from_admin_true_if_not_set(self, mock_get_user_from_message):
        settings.ADMINS = '*'
        mock_get_user_from_message.return_value = self.message
        self.assertTrue(RosterMixin().message_is_from_admin(self.message))

    @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    def test_message_is_from_admin_true_if_enlisted(self, mock_get_user_from_message):
        settings.ADMINS = ['wooh']
        mock_get_user_from_message.return_value = self.message
        self.assertTrue(RosterMixin().message_is_from_admin(self.message))

    @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    def test_message_is_from_admin_false_if_not_enlisted(self, mock_get_user_from_message):
        settings.ADMINS = ['skoczen']
        mock_get_user_from_message.return_value = self.message
        self.assertFalse(RosterMixin().message_is_from_admin(self.message))

    @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    def test_message_is_from_admin_false_if_not_lowercase(self, mock_get_user_from_message):
        settings.ADMINS = ['WoOh']
        mock_get_user_from_message.return_value = self.message
        self.assertFalse(RosterMixin().message_is_from_admin(self.message))


class TestAclSettings(unittest.TestCase):

    def setUp(self):
        settings.ACL_ONE = ["a", "b"]

    def test_get_acl_settings_name(self):
        self.assertEqual(get_acl_settings_name("one"), "ACL_ONE")
        self.assertEqual(get_acl_settings_name("two_two"), 'ACL_TWO_TWO')

    def test_get_acl_members(self):
        self.assertEqual(get_acl_members("one"), settings.ACL_ONE)
        self.assertEqual(get_acl_members("not_set"), [])


class TestVerifyAcl(unittest.TestCase):

    def setUp(self):
        settings.ACL_ENGINEERING_OPS = ["bob", "alice"]
        settings.ACL_ENGINEERING_DEVS = ["eve"]

    def test_is_acl_allowed_returns_true(self):
        self.assertTrue(is_acl_allowed("bob", {"engineering_ops"}))
        self.assertTrue(is_acl_allowed("alice", {"engineering_ops"}))
        self.assertTrue(is_acl_allowed("eve", {"engineering_devs"}))
        self.assertTrue(is_acl_allowed("eve", {"engineering_ops", "engineering_devs"}))
        self.assertTrue(is_acl_allowed("alice", {"engineering_ops", "engineering_devs"}))

    def test_is_acl_allowed_returns_false(self):
        self.assertFalse(is_acl_allowed("eve", {"engineering_ops"}))
        self.assertFalse(is_acl_allowed("bob", {"engineering_devs"}))
        self.assertFalse(is_acl_allowed("alice", {"engineering_devs"}))
        self.assertFalse(is_acl_allowed("bob", {"empty_acl"}))
