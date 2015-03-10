import unittest

from will.mixins.roster import RosterMixin
from will import settings
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