from mock import MagicMock, patch
import unittest

from will.plugins.friendly.talk_back import TalkBackPlugin


class TestTalkBackPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = TalkBackPlugin()

    @patch('requests.get')
    def test_get_quote_failure(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)

        with self.assertRaises(Exception):
            quote = self.plugin.get_quote()

            mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
            self.assertEqual(None, quote)

    @patch('requests.get')
    def test_get_quote_response_not_json(self, mock_get):
        mock_json = MagicMock(side_effect=ValueError())
        mock_get.return_value = MagicMock(status_code=200, json=mock_json)

        with self.assertRaises(Exception):
            quote = self.plugin.get_quote()

            mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
            self.assertEqual(None, quote)

    @patch('requests.get')
    def test_get_quote_invalid_response_format(self, mock_get):
        data = {'text': 'Hi!', 'author': 'An'}
        mock_json = MagicMock(return_value=data)
        mock_get.return_value = MagicMock(status_code=200, json=mock_json)

        with self.assertRaises(Exception):
            quote = self.plugin.get_quote()

            mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
            self.assertEqual(None, quote)

    @patch('requests.get')
    def test_get_quote_success(self, mock_get):
        data = {'results': [{'text': 'Hi!', 'author': 'An'}]}
        mock_json = MagicMock(return_value=data)
        mock_get.return_value = MagicMock(status_code=200, json=mock_json)

        quote = self.plugin.get_quote()

        mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
        self.assertEqual('Hi! ~ An', quote)

    @patch('will.plugin.WillPlugin.reply')
    @patch('requests.get')
    def test_talk_back_no_quote(self, mock_get, mock_reply):
        mock_json = MagicMock(return_value={})
        mock_get.return_value = MagicMock(status_code=200, json=mock_json)

        with self.assertRaises(Exception):
            self.plugin.talk_back("That's what she said")

            mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
            self.assertFalse(mock_reply.called)

    @patch('will.plugin.WillPlugin.reply')
    @patch('requests.get')
    def test_talk_back_success(self, mock_get, mock_reply):
        data = {'results': [{'text': 'Hi!', 'author': 'An'}]}
        mock_json = MagicMock(return_value=data)
        mock_get.return_value = MagicMock(status_code=200, json=mock_json)

        self.plugin.talk_back("That's what she said")

        mock_get.assert_called_once_with(TalkBackPlugin.QUOTES_URL)
        mock_reply.assert_called_once_with("That's what she said", 'Actually, she said things like this: \nHi! ~ An')
