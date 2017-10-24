import unittest

from will.mixins.roster import RosterMixin
from will import settings
from will.acl import is_acl_allowed
from mock import patch


class TestIsAdmin(unittest.TestCase):

    def setUp(self):
        self.message = {'nick': 'WoOh'}

    # TODO: Decide if we're keeping is_admin at all, and if so,
    # create new version of this that's properly abstracted, instead of get_user_from_message
    # @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    # def test_message_is_from_admin_true_if_not_set(self, mock_get_user_from_message):
    #     settings.ADMINS = '*'
    #     mock_get_user_from_message.return_value = self.message
    #     self.assertTrue(RosterMixin().message_is_from_admin(self.message))

    # @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    # def test_message_is_from_admin_true_if_enlisted(self, mock_get_user_from_message):
    #     settings.ADMINS = ['wooh']
    #     mock_get_user_from_message.return_value = self.message
    #     self.assertTrue(RosterMixin().message_is_from_admin(self.message))

    # @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    # def test_message_is_from_admin_false_if_not_enlisted(self, mock_get_user_from_message):
    #     settings.ADMINS = ['skoczen']
    #     mock_get_user_from_message.return_value = self.message
    #     self.assertFalse(RosterMixin().message_is_from_admin(self.message))

    # @patch('will.mixins.roster.RosterMixin.get_user_from_message')
    # def test_message_is_from_admin_false_if_not_lowercase(self, mock_get_user_from_message):
    #     settings.ADMINS = ['WoOh']
    #     mock_get_user_from_message.return_value = self.message
    #     self.assertFalse(RosterMixin().message_is_from_admin(self.message))


class TestVerifyAcl(unittest.TestCase):

    def setUp(self):
        settings.ACL = {
            "ENGINEERING_OPS": ["bob", "Alice"],
            "engineering_devs": ["eve"]
        }

    def test_is_acl_allowed_returns_true(self):
        self.assertTrue(is_acl_allowed("bob", {"engineering_ops"}))
        self.assertTrue(is_acl_allowed("alice", {"engineering_ops"}))
        self.assertTrue(is_acl_allowed("eve", {"engineering_devs"}))
        self.assertTrue(is_acl_allowed("eve", {"engineering_ops", "engineering_devs"}))
        self.assertTrue(is_acl_allowed("alice", {"engineering_ops", "engineering_devs"}))
        self.assertTrue(is_acl_allowed("Alice", {"engineering_ops", "engineering_devs"}))

    def test_is_acl_allowed_returns_false(self):
        self.assertFalse(is_acl_allowed("eve", {"engineering_ops"}))
        self.assertFalse(is_acl_allowed("bob", {"engineering_devs"}))
        self.assertFalse(is_acl_allowed("alice", {"engineering_devs"}))
        self.assertFalse(is_acl_allowed("bob", {"empty_acl"}))
